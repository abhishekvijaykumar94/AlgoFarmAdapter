import json
import sys
import threading
import time
import traceback
from datetime import datetime

from algoLibs import OrderDataQuery, QueryExecutorData, Trade, Product, CommonUtils, RepositoryInfo, OrderDataObject
from algoLibs.dao import DataRepository
from algoLibs.data_objects.trade_data_object import TradeDataObject
from algoLibs.live_trading import FillEvent
from algoLibs.utils import Logger
from confluent_kafka import Producer

from algoFarmAdapter.order_management.order_requests import Order, PlaceOrderResponse
from algoFarmAdapter.converter.order_data_converter import OrderDataConverter
from algoFarmAdapter.order_management import OrderResponse, OrderStatus
from algoFarmAdapter.web_socket import SmartWebSocketOrderUpdate

log = Logger(__name__, log_file=True)
exit_event= threading.Event()

class SmartAPIOrderListener:

    def __init__(self,api_key,session_data,feed_token,kafka_topic,bootstrap_servers):
        self.api_key = api_key
        self.username = session_data['data']['clientcode']
        self.auth_token = session_data['data']['jwtToken']
        self.refreshToken = session_data['data']['refreshToken']
        self.feed_token = feed_token
        self.sws = SmartWebSocketOrderUpdate(self.auth_token, self.api_key, self.username, self.feed_token)
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'batch.size': 163840,
            'linger.ms': 100,
            'max.in.flight.requests.per.connection': 10
        }
        self.market_data_producer = Producer(self.producer_config)
        self.market_data_producer.flush(timeout=1)
        self.kafka_topic = kafka_topic
        self.data_repository = DataRepository()
        self.order_data_converter =OrderDataConverter()

    def disconnect(self):
        self.sws.close_connection()
        self.sws.exit()

    def on_open(self, wsapp):
        print("on open")
        self.sws.subscribe("new_access1", 3, self.tokenList)

    def on_error(self, wsapp, error):
        print(error)

    def on_close(self, wsapp):
        print("Close")


    def on_data(self, wsapp, order_data_str,data_type, continue_flag):
        try:
            if exit_event.is_set():
                self.sws.close_connection()
                sys.exit()
            if data_type ==1:
                order_json = json.loads(order_data_str)
                order_json=self.replace_hyphens(order_json)
                if order_json["orderData"]["variety"] != "":
                    place_order_response = OrderResponse.from_json(order_json)
                    log.info("Received Order Response with status: %s",OrderStatus[place_order_response.order_status].value)
                    log.info("Full Order Message %s", order_data_str)
                    order_business_object = self.fetch_order(place_order_response.orderData.orderid)
                    order_json["orderData"]["strategy"] = order_business_object.strategy
                    updated_business_object = Order(**order_json["orderData"])
                    updated_business_object.id=order_business_object.id
                    repositoryInfo = RepositoryInfo(0.0)

                    if place_order_response.order_status == OrderStatus.AB05.name:

                        updated_business_object_str = CommonUtils.convert_data_class_to_json_str(updated_business_object)
                        fill_event = FillEvent(updated_business_object.strategy, datetime.now(), updated_business_object_str)
                        # self.market_data_producer.produce(fill_event.eventType, json.dumps(fill_event.to_dict()))
                        # self.market_data_producer.poll(0)
                        trade = Trade(trading_symbol=place_order_response.orderData.tradingsymbol,
                                      direction=place_order_response.orderData.transactiontype,
                                      product_type =Product.EQUITY_CASH,
                                      quantity=place_order_response.orderData.filledshares,
                                      entry_price=place_order_response.orderData.averageprice,
                                      order_id=place_order_response.orderData.orderid,
                                      fees=0.0,#TODD get fees from Smart API
                                      entry_date= datetime.now(),
                                      )

                        trade_data_object = TradeDataObject(trade)
                        log.info("Persisting trade %s", CommonUtils.convert_data_class_to_json_str(trade))
                        self.data_repository.save(trade_data_object,repositoryInfo)
                    order_business_object_list=[]
                    order_business_object_list.append(updated_business_object)
                    order_data_object = OrderDataObject(self.order_data_converter.to_data_object(order_business_object_list))
                    log.info("Persisting order %s", CommonUtils.convert_data_class_to_json_str(updated_business_object))
                    self.data_repository.save(order_data_object, repositoryInfo)


        except Exception as e:
            log.error("Error while processing order:\n%s",order_data_str)
            log.error("Exception:\n%s", traceback.format_exc())
            log.error("stack trace:\n%s", traceback.format_exc())


    def replace_hyphens(self, obj):
        """Recursively replaces hyphens with underscores in dictionary keys."""
        if isinstance(obj, dict):
            return {key.replace("-", "_"): self.replace_hyphens(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_hyphens(item) for item in obj]
        else:
            return obj

    import time

    def fetch_order(self, order_id: str) -> Order:
        order_id_list = [order_id]
        max_attempts = 3  # Maximum number of retries
        wait_time = 3  # Wait time (in seconds) before retrying

        for attempt in range(max_attempts):
            order_data_objects = self.data_repository.query(
                OrderDataQuery(order_ids=order_id_list),
                query_executor_data=QueryExecutorData("-1hr")
            )

            if order_data_objects:  # Check if the order exists in the database
                order_business_objects = self.order_data_converter.to_business_object(order_data_objects)
                return order_business_objects[0]  # Return order if found
            else:
                log.info(f"Order not available, running attempt {attempt + 1}/{max_attempts}, waiting {wait_time} seconds before retrying.")
            if attempt < max_attempts - 1:
                time.sleep(wait_time)  # Wait before retrying
            else:
                raise Exception(f"Order {order_id} not found after {max_attempts} attempts.")


    def _on_pong(self, wsapp, data):
        print("In on pong function==> ", data)
        # print("Checking market timings")T
        ct = datetime.utcnow().time().strftime("%H:%M")
        if ct > '10:00':
            print("Post market hours")
            exit_event.set()

    def connect(self):
        self.sws.on_open = self.on_open
        self.sws.on_data = self.on_data
        self.sws.on_error = self.on_error
        self.sws.on_close = self.on_close
        self.sws._on_pong = self._on_pong
        self.sws.connect()

    def start(self):
        con = threading.Thread(target=self.connect)
        con.start()