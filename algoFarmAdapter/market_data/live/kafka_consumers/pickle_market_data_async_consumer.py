import os
import pickle
import time

from algoLibs.converters.smart_api_converter import MarketDataConverter
from algoLibs.market_data_stream import MarketDataConsumerAsync
from algoLibs.utils import CommonUtils


class PickleMarketDataAsyncConsumer(MarketDataConsumerAsync):

    def __init__(self,  kafka_topic:str, bootstrap_servers:str, kafka_group_id:str, market_data_converter:MarketDataConverter,
                 batch_size=5000, flush_interval=20):
        super().__init__(kafka_topic, bootstrap_servers, kafka_group_id, market_data_converter,batch_size,flush_interval)
        self.pickle_output_path=CommonUtils.getFilePathOutputDirectory()

    async def output_Data(self,batch_data):
        # df = self.marketDataOperations.extract_features(batchData)
        t = int(time.time())
        file_path = os.path.join(self.pickle_output_path, 'example{}.pkl'.format(t))
        with open(file_path, 'wb') as f:
            pickle.dump(batch_data, f)



