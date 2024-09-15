import json
import sys
import time
from datetime import datetime
from typing import Dict

import numpy as np
from algoLibs.utils import Logger
from confluent_kafka import Producer
import threading
import logging

from algoFarmAdapter.web_socket import SmartWebSocketV2

log = Logger(__name__, log_file=True)
exit_event= threading.Event()
class MockMarketDataFeeder:

    def __init__(self, api_key:str,session_data:Dict,kafka_topic:str,bootstrap_servers:str,feed_token:str,batch_size:int):

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
        self.market_data_producer.flush(timeout=1)
        self.counter=0
        self.batch_size=batch_size

    def getMarketQuoteList(self):
        quote_list = []
        for i in range(250):
            delta_t = 0.001
            time.sleep(delta_t)
            norm = np.random.normal(1)
            mu = 0.07
            sigma = 0.05
            tt = delta_t / 252
            ret = mu * tt + sigma * np.sqrt(tt) * norm
            current_time = int(datetime.utcnow().timestamp())
            price = 100.0 * np.exp(ret)
            # Create a dictionary for the message
            msg = {
                "subscription_mode": 2,
                "exchange_type": 3,
                "token": "500325",
                "sequence_number": 3512686,
                "exchange_timestamp": current_time,
                "last_traded_price": price,
                "subscription_mode_val": "QUOTE",
                "open_interest":0,
                "last_traded_quantity": 1,
                "average_traded_price": 286121,
                "volume_trade_for_the_day": 31509,
                "total_buy_quantity": 33072.0,
                "total_sell_quantity": 187950.0,
                "open_price_of_the_day": 285105,
                "high_price_of_the_day": 287390,
                "low_price_of_the_day": 284805,
                "closed_price": 285075,
                "best_5_buy_data": [
                    {"flag": 0, "quantity": 50, "price": 2209660, "no of orders": 1},
                    {"flag": 0, "quantity": 200, "price": 2209700, "no of orders": 4},
                    {"flag": 0, "quantity": 300, "price": 2209800, "no of orders": 6},
                    {"flag": 0, "quantity": 50, "price": 2209850, "no of orders": 1},
                    {"flag": 0, "quantity": 1000, "price": 2209900, "no of orders": 7},
                ],
                "best_5_sell_data": [
                    {"flag": 1, "quantity": 1500, "price": 2209600, "no of orders": 1},
                    {"flag": 1, "quantity": 50, "price": 2209400, "no of orders": 1},
                    {"flag": 1, "quantity": 250, "price": 2209345, "no of orders": 1},
                    {"flag": 1, "quantity": 100, "price": 2209300, "no of orders": 2},
                    {"flag": 1, "quantity": 100, "price": 2209230, "no of orders": 1},
                ],

            }
            # Convert dictionary to JSON string
            json_msg = json.dumps(msg)
            quote_list.append(json_msg)
        return quote_list

    def start(self):
        quote_list = self.getMarketQuoteList()
        while True:
            for json_string in quote_list:
                self.market_data_producer.produce(self.kafkaTopic, json_string)
                self.counter += 1
                if (self.counter % self.batch_size == 0):
                    self.market_data_producer.poll(0)
                    log.info("Sent a total of {:,} Messages at {}".format(self.counter, datetime.utcnow().time()))
            time.sleep(1)


