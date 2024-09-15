import sys
import threading
import traceback

from algoLibs.dao import DataRepository
from algoLibs.data_objects import OrderDataObject
from algoLibs.live_trading import FillEvent
from algoLibs.utils import Logger
from confluent_kafka import Producer
from datetime import datetime

from algoFarmAdapter.order_management import OrderResponse, OrderStatus
from algoFarmAdapter.web_socket import SmartWebSocketOrderUpdate
import json

log = Logger(__name__, log_file=True)
exit_event= threading.Event()

class SmartAPIOrderListener:

    def __init__(self,api_key,session_data,feed_token,kafka_topic,bootstrap_servers,data_repository:DataRepository):
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
        self.data_repository = data_repository

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

    def on_data(self, wsapp, order_data_str):
        try:
            if exit_event.is_set():
                self.sws.close_connection()
                sys.exit()
            order_json = json.loads(order_data_str)
            order_response = OrderResponse(**order_json)
            order_data_object = OrderDataObject(data=order_response)
            self.data_repoistory.save(order_data_object, None)

            if order_response.order_status == OrderStatus.AB05:
                # orderDataQuery = OrderDataQuery(
                #     tag_string="uniqueorderid",
                #     tags=[order_response.orderData.uniqueorderid],
                #     n=1,
                #     add_pivot=True)
                # orderDataList = self.data_repoistory.query(orderDataQuery, None)
                # orderDataList[0].strategyid
                fill_event = FillEvent("strategy_id",datetime.now(),order_data_str)
                self.market_data_producer.produce(self.kafka_topic,json.dumps(fill_event.to_dict()))
                self.market_data_producer.poll(0)
        except Exception as e:
            log.exception("Error while processing order:\n%s",order_data_str)
            log.exception("Exception:\n%s", traceback.format_exc())
            log.exception("stack trace:\n%s", traceback.format_exc())

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