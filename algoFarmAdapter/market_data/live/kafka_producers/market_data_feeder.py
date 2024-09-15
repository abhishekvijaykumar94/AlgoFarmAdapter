import json
import sys
from datetime import datetime
from typing import List, Dict

from algoLibs.utils import Logger
from confluent_kafka import Producer
import threading
import logging

from algoFarmAdapter.web_socket import SmartWebSocketV2

log = Logger(__name__, log_file=True)
exit_event= threading.Event()
class MarketDataFeeder:

    def __init__(self, api_key:str,session_data:Dict,kafka_topic:str,bootstrap_servers:str,feed_token:str,token_list:List[int],batch_size:int):

        self.api_key = api_key
        self.username = session_data['data']['clientcode']
        self.auth_token = session_data['data']['jwtToken']
        self.refreshToken = session_data['data']['refreshToken']
        self.feed_token = feed_token
        self.sws = SmartWebSocketV2(self.auth_token, self.api_key, self.username, self.feed_token)
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'batch.size': 163840,
            'linger.ms': 100,
            'max.in.flight.requests.per.connection':10
        }
        self.market_data_producer = Producer(self.producer_config)
        self.kafka_topic = kafka_topic
        self.token_list=token_list
        self.market_data_producer.flush(timeout=1)
        self.counter=0
        self.batch_size=batch_size

    def disconnect(self):
        self.sws.close_connection()
        self.sws.exit()

    def on_open(self,wsapp):
        print("on open")
        self.sws.subscribe("new_access1", 3, self.token_list)

    def on_error(self,wsapp, error):
        print(error)

    def on_close(self,wsapp):
        print("Close")

    def on_data(self, wsapp, message):
        try:
            if exit_event.is_set():
                self.sws.close_connection()
                sys.exit()
            json_string = json.dumps(message)
            self.market_data_producer.produce(self.kafka_topic, json_string)
            self.counter += 1
            if (self.counter % self.batch_size == 0):
                self.market_data_producer.poll(0)
                log.info("Sent a total of {:,} Messages at {}".format(self.counter, datetime.utcnow().time()))
                # print("Sent a total of {:,} Messages at {}".format(self.counter, datetime.utcnow().time()))
        except Exception as e:
            logging.exception("An error occurred: {}".format(e))

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
        con = threading.Thread(target = self.connect)
        con.start()


