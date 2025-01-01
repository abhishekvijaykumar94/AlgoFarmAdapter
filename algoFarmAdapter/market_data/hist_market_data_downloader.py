import gc
import os
from datetime import datetime

import pandas as pd
from algoLibs import RepositoryInfo, EquityMarketDataObject
from algoLibs.file_processors.date_range_processor import DateRangeProcessor
from algoLibs.market_data_stream.connection_manager.boto_connection_manager import BotoConnectionManager
from algoLibs.utils.common_utils import CommonUtils
from pandas import json_normalize

from algoFarmAdapter.converter.smart_api_equity_market_data_converter import SmartApiEquityMarketDataConverter


class HistMarketDataDownloader(DateRangeProcessor):

    def __init__(self, start_date, end_date, influxdb_client_manager, bucket_name, batch_size):
        super().__init__(start_date, end_date, influxdb_client_manager)
        self.batch_size = batch_size
        self.connection = BotoConnectionManager(bucket_name)
        self.all_files = self.connection.list_files_in_bucket()
        self.hist_mkt_data_output_dir = CommonUtils.get_hist_mkt_data_file_path_output_directory()

    def process_nested_json(self, unprocessed_df):
        fields_df = json_normalize(unprocessed_df['fields'].tolist())
        unprocessed_df['sym_token'] = unprocessed_df['tags'].apply(lambda x: x['sym_token'])
        merged_df = pd.merge(
            unprocessed_df[['sym_token', 'time']], fields_df, left_index=True, right_index=True, how='inner'
        )
        return merged_df

    def process(self, date):
        date_str = 'Market_Data_' + date.strftime("%Y%m%d") + '.7z'
        repository_info = RepositoryInfo(cache_domain=False, database_domain=True)
        smart_api_mkt_data_converter = SmartApiEquityMarketDataConverter()
        for file_name in self.all_files:
            if date_str in file_name:
                try:
                    output_directory_path = os.path.join(self.hist_mkt_data_output_dir, file_name)
                    # equity_market_data_operations = EquityMarketDataInfluxDbOperations(self.hist_mkt_data_output_dir)
                    local_filename = file_name.split('/')[-1]
                    local_file_path = os.path.join(self.hist_mkt_data_output_dir, local_filename)

                    if not os.path.exists(local_file_path):
                        print(f'Downloading {file_name} to {local_filename}')
                        self.connection.download_object(file_name, output_directory_path)
                        CommonUtils.extract_data_from_7zip_to_current_path(
                            output_directory_path, self.hist_mkt_data_output_dir
                        )
                    else:
                        print(f'File {local_filename} already exists, skipping download.')
                        migration_token_processor = None

                    filter_date = pd.to_datetime(file_name.split('_')[2].split('.')[0], format='%Y%m%d')
                    token_symbol_map = migration_token_processor.get_migration_token_to_symbol_dict(filter_date)

                    all_pkl_files = [
                        f for f in os.listdir(self.hist_mkt_data_output_dir) if f.endswith('.pkl')
                    ]
                    file_counter = 0
                    dbfile_list = []

                    for dbfile_name in all_pkl_files:
                        if dbfile_name.endswith('.pkl'):
                            dbfile = CommonUtils.load_pickle_file(self.mkt_data_output_dir,'/' + dbfile_name)
                            dbfile_list.extend(dbfile)
                            file_counter += 1

                            if file_counter % self.batch_size == 0 or dbfile_name == all_pkl_files[-1]:
                                print(f"Processed {file_counter:,} pkl files for {file_name} at {datetime.utcnow().time()}")
                                ticks_df = pd.DataFrame(dbfile_list)
                                result_df = self.process_nested_json(ticks_df)
                                result_df['token_int'] = result_df['sym_token'].astype(int)
                                result_df['symbol'] = result_df['token_int'].map(token_symbol_map)

                                missing_symbols = result_df[result_df['symbol'].isnull()]['token_int'].unique()
                                print(f"Completed Pre-Processing at {datetime.utcnow().time()}")

                                if len(missing_symbols) > 0:
                                    print(f"Missing symbols for tokens: {missing_symbols}")

                                points = smart_api_mkt_data_converter.convert_to_native_format(result_df)

                                equityMarketDataOject = EquityMarketDataObject(points)
                                self.data_repository.save(repository_info, equityMarketDataOject)

                                del result_df, dbfile_list
                                gc.collect()
                                dbfile_list = []

                except Exception as e:
                    print(f"Error while processing data for file {file_name}")
                    CommonUtils.log_error_details(e)

                CommonUtils.clear_all_data_from_path(CommonUtils.get_hist_mkt_data_file_path_output_directory())
