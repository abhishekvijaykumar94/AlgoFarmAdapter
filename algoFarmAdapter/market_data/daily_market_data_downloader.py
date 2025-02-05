import asyncio
import gc
import os
from datetime import datetime

import pandas as pd
from algoLibs import DataRepository, EquityMarketDataObject, RepositoryInfo, TickMarketFeedColumns
from algoLibs.file_processors.date_range_processor import DateRangeProcessor
from algoLibs.market_data_stream.connection_manager.boto_connection_manager import BotoConnectionManager
from algoLibs.utils.common_utils import CommonUtils
from pandas import json_normalize

from algoFarmAdapter.converter.smart_api_equity_market_data_converter import SmartApiEquityMarketDataConverter, \
    SmartApiInputFields
from algoFarmAdapter.file_processors.token_mapping_processor import TokenMappingProcessor

pd.set_option('display.max_colwidth', 1000)
pd.set_option('display.max_columns', None)


class DailyMarketDataDownloader(DateRangeProcessor):

    def __init__(self, start_date, end_date, influxdb_client_manager, bucket_name, batch_size):
        super().__init__(start_date, end_date, influxdb_client_manager)
        self.batch_size = batch_size
        self.connection = BotoConnectionManager(bucket_name)
        self.all_files = self.connection.list_files_in_bucket()
        self.mkt_data_output_dir = CommonUtils.get_file_path_output_directory()
        self.data_repository = DataRepository()

    def process_nested_json(self, unprocessed_df):
        fields_df = json_normalize(unprocessed_df['fields'].tolist())
        unprocessed_df['sym_token'] = unprocessed_df['tags'].apply(lambda x: x['sym_token'])
        merged_df = pd.merge(
            unprocessed_df[['sym_token', 'time']], fields_df, left_index=True, right_index=True, how='inner'
        )
        return merged_df

    def process(self, date):
        dbfile_list = []
        date_str = 'Market_Data_' + date.strftime("%Y%m%d") + '.7z'
        repository_info = RepositoryInfo(cache_domain=False,database_domain=True)
        smart_api_mkt_data_converter = SmartApiEquityMarketDataConverter()
        for file_name in self.all_files:
            if date_str in file_name:
                try:
                    output_directory_path = os.path.join(self.mkt_data_output_dir, file_name)
                    # equity_market_data_operations = EquityMarketDataInfluxDbOperations(self.mkt_data_output_dir)
                    local_filename = file_name.split('/')[-1]
                    local_file_path = os.path.join(self.mkt_data_output_dir, local_filename)

                    if not os.path.exists(local_file_path):
                        self.connection.download_object(file_name, output_directory_path)
                        CommonUtils.extract_data_from_7zip_to_current_path(output_directory_path, self.mkt_data_output_dir)

                    else:
                        print(f'File {local_filename} already exists, skipping download.')
                        migration_token_processor = None
                    token_mapping_processor = TokenMappingProcessor("Token_mapping.csv",self.mkt_data_output_dir)
                    token_symbol_map = token_mapping_processor.get_token_to_symbol_dict()
                    # filter_date = pd.to_datetime(file_name.split('_')[2].split('.')[0], format='%Y%m%d')
                    # token_symbol_map = migration_token_processor.get_migration_token_to_symbol_dict(filter_date)

                    all_pkl_files = [
                        f for f in os.listdir(self.mkt_data_output_dir) if f.endswith('.pkl')
                    ]
                    file_counter = 0

                    for dbfile_name in all_pkl_files:
                        if dbfile_name.endswith('.pkl'):
                            dbfile = CommonUtils.load_pickle_file(self.mkt_data_output_dir,'/' + dbfile_name)
                            dbfile_list.extend(dbfile)
                            file_counter += 1

                            if file_counter % self.batch_size == 0 or dbfile_name == all_pkl_files[-1]:
                                print(f"Processed {file_counter:,} pkl files for {file_name} at {datetime.utcnow().time()}")
                                ticks_df = pd.DataFrame(dbfile_list)
                                ticks_df['token_int'] = ticks_df['token'].astype(int)
                                ticks_df['symbol'] = ticks_df['token_int'].map(token_symbol_map)

                                missing_symbols = ticks_df[ticks_df['symbol'].isnull()]['token_int'].unique()

                                if len(missing_symbols) > 0:
                                    print(f"Missing symbols for tokens: {missing_symbols}")

                                points = smart_api_mkt_data_converter.convert_to_native_format(ticks_df)

                                equity_market_data_object = EquityMarketDataObject(data=points,
                                                                            time_series=ticks_df[SmartApiInputFields.exchange_timestamp],
                                                                            data_key=ticks_df[TickMarketFeedColumns.tag])
                                self.data_repository.save(equity_market_data_object,repository_info)

                                del ticks_df, dbfile_list
                                gc.collect()
                                dbfile_list = []

                except Exception as e:
                    print(f"Error while processing data for file {file_name}")
                    CommonUtils.log_error_details(e)

                CommonUtils.clear_all_data_from_path(self.mkt_data_output_dir)
