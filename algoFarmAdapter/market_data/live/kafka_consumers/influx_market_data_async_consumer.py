import pandas as pd
from algoLibs.converters.smart_api_converter import MarketDataConverter
from algoLibs.dao import InfluxDBClientManager
from algoLibs.market_data_stream.kafka_consumers.market_data_consumer_async import MarketDataConsumerAsync

class InfluxMarketDataAsyncConsumer(MarketDataConsumerAsync):

    def __init__(self, kafka_topic, bootstrap_servers, kafka_group_id,token_mapping_df, market_data_converter:MarketDataConverter,
                 influxdb_client_manager:InfluxDBClientManager,batch_size=10000, flush_interval=30):
        super().__init__(kafka_topic,bootstrap_servers,kafka_group_id,market_data_converter,batch_size,flush_interval)
        self.token_mapping_df=token_mapping_df
        self.influxdb_client_manager=influxdb_client_manager

    async def output_Data(self,batch_data):
        batch_df = pd.DataFrame(batch_data)
        token_mapping_df_copy = self.token_mapping_df.copy()
        token_mapping_df_copy['token'] = token_mapping_df_copy['token'].astype(str)
        merged_df = pd.merge(batch_df, token_mapping_df_copy, on='token', how='left')
        points = self.market_data_converter.convert_input_df_to_persistable_str_list(merged_df)
        await self.influxdb_client_manager.write_data_async(points)


