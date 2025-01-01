import json
from typing import Dict, List

import pandas as pd
from algoLibs import TickMarketFeedColumns
from algoLibs.dao import DataRepository
from algoLibs.data_objects import RepositoryInfo
from algoLibs.data_objects.equity_market_data_object import EquityMarketDataObject
from algoLibs.market_data_stream.kafka_consumers.market_data_consumer_async import MarketDataConsumerAsync
from algoLibs.utils.common_utils import CommonUtils

from algoFarmAdapter.converter.smart_api_equity_market_data_converter import SmartApiEquityMarketDataConverter, \
    SmartApiInputFields


class LiveMarketDataRedisConsumer(MarketDataConsumerAsync):

    def __init__(self, kafka_topic:str, bootstrap_servers:str, kafka_group_id:str,token_symbol_map:Dict,
                 retention_seconds, batch_size=5000, flush_interval=20):
        super().__init__(kafka_topic, bootstrap_servers, kafka_group_id, batch_size, flush_interval)
        self.pickle_output_path = CommonUtils.getFilePathOutputDirectory()
        self.retention_seconds = retention_seconds
        self.token_symbol_map = token_symbol_map
        self.object_key = EquityMarketDataObject.__name__
        self.data_repoistory = DataRepository()
        self.smartApiEquityMarketDataConverter = SmartApiEquityMarketDataConverter()

    async def output_Data(self, batch_data:List[json]):
        repository_info = RepositoryInfo(retention_seconds=self.retention_seconds,converter=self.smartApiEquityMarketDataConverter)
        batch_data_df = pd.DataFrame(batch_data)
        batch_data_df['symbol'] = batch_data_df['token'].astype(int).map(self.token_symbol_map)
        native_json_list = self.smartApiEquityMarketDataConverter.convert_to_native_format(batch_data_df)
        equity_market_data = EquityMarketDataObject(data=native_json_list,time_series=batch_data_df[SmartApiInputFields.exchange_timestamp],
                                                    data_key=batch_data_df[TickMarketFeedColumns.tag])
        self.data_repoistory.save(equity_market_data, repository_info)
