import json
import os
import time
from datetime import datetime

import pandas as pd
from algoLibs import DateRangeProcessor, BotoConnectionManager, CommonUtils, PropertyManager, AppConstants, \
    RepositoryInfo, TickerSubscription, TickerSubscriptionDO, DataRepository

from algoFarmAdapter.file_processors.token_mapping_processor import TokenMappingProcessor

pd.set_option('display.max_colwidth', 1000)
pd.set_option('display.max_columns', None)

from confluent_kafka import Producer

class LiveMarketDataSimulator(DateRangeProcessor):

    def __init__(self, start_date, end_date, influx_client_manager, bucket_name, kafkaTopic):
        super().__init__(start_date, end_date, influx_client_manager)
        self.connection = BotoConnectionManager(bucket_name)
        self.all_files = self.connection.list_files_in_bucket()
        self.mktDataOutputDir = CommonUtils.get_file_path_output_directory()
        self.data_repository = DataRepository()
        self.producer_config = {
            'bootstrap.servers': PropertyManager.getValue(AppConstants.BOOTSTRAP_SERVERS),
            'batch.size': 163840,
            'linger.ms': 100,
            'max.in.flight.requests.per.connection': 10
        }
        self.marketDataProducer = Producer(self.producer_config)
        self.marketDataProducer.flush(timeout=1)
        self.kafkaTopic = kafkaTopic
        self.token_mapping_processor = None

    def timestamp_to_datetime(self,timestamp):
        return datetime.utcfromtimestamp(timestamp / 1000.0)

    def publish_message(self,message):
        json_string = json.dumps(message)
        self.marketDataProducer.produce(self.kafkaTopic, json_string)
        self.marketDataProducer.poll(0)

    def save_subscription_symbols(self, subscribed_symbol_list, subscribed_token_list):
        current_datetime = datetime.now()
        ticker_subscription_list = []
        repository_info = RepositoryInfo(cache_domain=False)

        for symbol, token in zip(subscribed_symbol_list, subscribed_token_list):
            ticker_subscription = TickerSubscription(
                ticker_symbol=symbol,
                token=token,  # Assuming you want to use the token here
                subscription_date=current_datetime
            )
            ticker_subscription_list.append(ticker_subscription)

        ticker_subscription_do = TickerSubscriptionDO(data=ticker_subscription_list)
        self.data_repository.save(ticker_subscription_do, repository_info)

    def process(self, date):
        date_str = 'Market_Data_' + date.strftime("%Y%m%d") + '.7z'
        for file_name in self.all_files:
            if (date_str in file_name):
                output_directory_path = os.path.join(self.mktDataOutputDir, file_name)
                local_filename = file_name.split('/')[-1]
                local_file_path = os.path.join(self.mktDataOutputDir, local_filename)
                current_time = datetime.now()

                if not os.path.exists(local_file_path):
                    print(f'Downloading {file_name} to {local_filename}')
                    self.connection.download_object(file_name, output_directory_path)
                    CommonUtils.extract_data_from_7zip_to_current_path(output_directory_path, self.mktDataOutputDir)
                    self.token_mapping_processor = TokenMappingProcessor("Token_mapping.csv", self.mktDataOutputDir)
                    symbol_list,token_list = self.token_mapping_processor.get_symbols_and_tokens()
                    self.save_subscription_symbols(symbol_list,token_list)
                    print("Completed writing subscribed symbols and tokens to Database")
                else:
                    print(f'File {local_filename} already exists, skipping download.')
                # CommonUtils.copy_file(self.mktDataOutputDir,CommonUtils.get_path_to_project_directory("data"),"Token_mapping.csv")

                all_pkl_files = [f for f in os.listdir(self.mktDataOutputDir) if
                                     f.endswith('.pkl')]
                all_pkl_files.sort(key=lambda f: int(f.split('example')[1].split('.')[0]))
                previous_timestamp = None
                for dbfileName in all_pkl_files:
                    message_count = 0
                    if dbfileName.endswith('.pkl'):
                        # print("Publishing all messages for file: ", dbfileName)
                        dbfile = CommonUtils.load_pickle_file(self.mktDataOutputDir,'/'+dbfileName)
                        print("Timestamp of the first message in the file ", dbfileName, " is ", current_time," actual time ", datetime.now())
                        for i, message in enumerate(dbfile):
                            message_count += 1
                            timestamp = message['exchange_timestamp']
                            current_time = self.timestamp_to_datetime(timestamp)
                            if previous_timestamp is None:
                                previous_timestamp = current_time
                            # if i == 0:  # Set the start time and previous timestamp for the first message in the dbfile
                            #
                            #     previous_timestamp = current_time
                            # else:
                            if current_time < previous_timestamp:
                                time_diff_seconds = 0
                            else:
                                time_diff = current_time - previous_timestamp
                                time_diff_seconds = time_diff.total_seconds()
                            if time_diff_seconds > 0:
                                if(time_diff_seconds>30.0):
                                    print("Putting thread to sleep for ",time_diff_seconds," seconds")
                                time.sleep(time_diff_seconds)
                            self.publish_message(message)
                            if previous_timestamp <= current_time:
                                previous_timestamp = current_time

                            # if message_count % 5000 == 0:
                            #     print("Total message count at ", timestamp, " for file ", dbfileName, " is ",message_count)

