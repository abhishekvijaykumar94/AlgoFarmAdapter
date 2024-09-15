from typing import Dict

import pandas as pd
from algoLibs.converters.smart_api_converter import MarketDataConverter
from algoLibs.dao import redis, __all__, DataRepository
from algoLibs.data_objects import RepositoryInfo
from algoLibs.data_objects.equity_market_data_object import EquityMarketDataObject
from algoLibs.market_data_stream.kafka_consumers.market_data_consumer_async import MarketDataConsumerAsync
from algoLibs.utils.common_utils import CommonUtils
from algoLibs.utils.property_manager import PropertyManager


class LiveMarketDataRedisConsumer(MarketDataConsumerAsync):

    def __init__(self, kafka_topic:str, bootstrap_servers:str, kafka_group_id:str, market_data_converter:MarketDataConverter,token_symbol_map:Dict,
                 retention_seconds, batch_size=5000, flush_interval=20):
        super().__init__(kafka_topic, bootstrap_servers, kafka_group_id, market_data_converter, batch_size, flush_interval)
        self.pickle_output_path = CommonUtils.getFilePathOutputDirectory()
        redis_port = PropertyManager.getValue('redis.server.port')
        self.r = redis.Redis(host='localhost', port=int(redis_port), db=0)
        self.retention_seconds = retention_seconds
        self.token_symbol_map = token_symbol_map
        self.object_key = EquityMarketDataObject.__name__
        self.data_repoistory = DataRepository()

    async def output_Data(self, batch_data):
        repository_info = RepositoryInfo(self.retention_seconds)
        batch_data_df = pd.DataFrame(batch_data)
        batch_data_df['symbol'] = batch_data_df['token'].astype(int).map(self.token_symbol_map)
        equity_market_data = EquityMarketDataObject(data=batch_data_df)
        self.data_repoistory.save(equity_market_data, repository_info)
        # for message in batchData:
        #     token = message["token"]
        #     message["symbol"] = self.tokenSymbolMap[int(token)]
        #     equity_market_data = EquityMarketDataObject(message)
        #     self.data_repoistory.save(equity_market_data,repository_info)
            # token = message["token"]
            # timestamp = message["exchange_timestamp"]
            # key = f"{self.object_key}_{symbol}"
            # # Store the JSON message in a Redis hash
            # self.r.hset(key, timestamp, json.dumps(message))
            # # Add the timestamp to a sorted set for the object key and symbol
            # sorted_set_key = f"sorted:{self.object_key}_{symbol}"
            # self.r.zadd(sorted_set_key, {timestamp: timestamp})
            #
            # # Set an expiration time for the hash and sorted set
            # self.r.expire(key, self.retention_seconds)
            # self.r.expire(sorted_set_key, self.retention_seconds)

# Example usage:
# if __name__ == "__main__":
#     consumer = LiveMarketDataRedisConsumer(
#         kafkaTopic="your_kafka_topic",
#         bootstrapServers="your_bootstrap_servers",
#         kafkaGroupId="your_kafka_group_id",
#         marketDataOperations=None  # Replace with actual operations if needed
#     )
#     # Assuming you have a way to consume data, otherwise integrate this consumer with your Kafka setup
