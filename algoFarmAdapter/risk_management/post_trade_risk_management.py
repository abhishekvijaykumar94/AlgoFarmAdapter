from datetime import datetime
import json
from collections import defaultdict
from typing import Dict, List

import algoLibs as libs
from algoLibs import Signal, TransactionType, FillEvent, Holding

from algoFarmAdapter import OrderResponse


class PostTradeRiskService(libs.CoreMicroService):

    def __init__(self, service_name, kafka_bootstrap_servers, consume_topics, token_symbol_map):
        super().__init__(
            service_name=service_name,
            kafka_bootstrap_servers=kafka_bootstrap_servers,
            kafka_consumer_callback=self.process_event,
            consume_topics=consume_topics
        )
        self.token_symbol_map = token_symbol_map
        self.data_repository = libs.DataRepository()
        # self.smartApiEquityMarketDataConverter = libs.SmartApiEquityMarketDataConverter()
        self.current_holdings: Dict[str, list(libs.Holding) ] = self.initialize_holdings()


    def initialize_holdings(self):
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        holding_data_query = libs.HoldingDataQuery(position_date=current_date)
        query_executor_data = libs.QueryExecutorData("-3hr")
        holding_data_list= self.data_repository.query(holding_data_query,query_executor_data)
        holdings_dict = defaultdict(list)
        for holding_data in holding_data_list:
            holdings_dict[holding_data.trading_symbol].append(
                libs.Holding(
                    trading_symbol=holding_data.trading_symbol,
                    quantity=holding_data.quantity,
                    acquisition_price=holding_data.acquisition_price,
                    position_value=holding_data.position_value,
                    strategy=holding_data.strategy,
                    position_date=str(holding_data.position_date) if holding_data.position_date else None
                )
            )
        return dict(holdings_dict)

    async def process_event(self, message):
        try:
            # Decode Kafka message
            json_str = message.value.decode('utf-8')
            data = json.loads(json_str)
            if "token" in data: #Means this is incoming market data
                symbol = self.token_symbol_map[data["token"]]
                holdings_list = self.current_holdings[symbol]
                if holdings_list:
                    await self.evaluate_risk(holdings_list,data)
            else: #This is FILL EVENT
                fill_event = FillEvent.from_json(json_str)
                order_response = fill_event.payload
                order_response = OrderResponse(**order_response)
                incremental_holding = Holding(trading_symbol=order_response.tradingsymbol,
                                  quantity=order_response.orderData.quantity,
                                  acquisition_price=order_response.orderData.averageprice,
                                  position_value=order_response.orderData.filledshares*order_response.order_data.averageprice,
                                  strategy=order_response.orderData.strategy)
                total_holding:Holding = self.holdings_dict[order_response.orderData.tradingsymbol]
                total_holding = total_holding.add_holding(incremental_holding)
                self.holdings_dict[order_response.orderData.tradingsymbol] = total_holding

        except Exception as e:
            self.logger.error(f"Error processing event: {e}", exc_info=True)


    async def run(self):
        await self.start_kafka()
        await self.consume_messages()

    async def evaluate_risk(self, holdings_list:List[libs.Holding],data):
        symbol = self.token_symbol_map[data["token"]]
        for holding in holdings_list:
            last_traded_price = data["last_traded_price"] / 100.0
            # TODO check if position is long or short in the more complex case
            strat_return = last_traded_price / holding.acquisition_price
            if strat_return < 0.8:
                signal = Signal(
                    _message_type="PlaceOrderRequest",
                    trading_symbol=symbol,
                    token=data["token"],
                    transaction_type=TransactionType.SHORT,
                    ordertype="MARKET",
                    duration="DAY",
                    quantity=holding.quantity,
                    signal_time=str(datetime.now()),
                    signal_id=int(datetime.now().timestamp() * 1000000),
                    strategy_id=holding.strategy
                )
                await self.publish_message(signal)

