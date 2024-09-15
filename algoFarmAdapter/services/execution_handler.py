import json
from dataclasses import asdict

# from algofarm.LiveTrading.OrderManagement.OrderRequests import PlaceOrderRequest, ModifyOrderRequest, \
#     CancelOrderRequest, PlaceOrderResponse, ModifyOrderResponse, CancelOrderResponse

from algoLibs.live_trading.events.events import EventType, Event
from algoLibs.live_trading.services.core_micro_service import CoreMicroService

from algoFarmAdapter.external.smart_api_connection_manager import SmartApiConnectionManager
from algoFarmAdapter.order_management import PlaceOrderRequest, ModifyOrderRequest, CancelOrderRequest, \
    PlaceOrderResponse, ModifyOrderResponse, CancelOrderResponse


class ExecutionHandler(CoreMicroService):


    def __init__(self, service_name, kafka_bootstrap_servers, api_key,consume_topic=EventType.Signal_Event):
        """
        ExecutionHandler class that extends the CoreMicroService to handle order execution.

        :param service_name: Name of the microservice.
        :param kafka_bootstrap_servers: Kafka bootstrap servers.
        :param api_key: API key to connect to the brokerage.
        :param sampling_frequency: Frequency in seconds for processing.
        :param consume_topic: The Kafka topic to consume SIGNAL events from.
        """
        super().__init__(service_name, kafka_bootstrap_servers)
        self.connection_manager = SmartApiConnectionManager(api_key)
        self.consume_topic = consume_topic

    async def run(self):
        """Main loop to process SIGNAL events and execute orders."""
        # Start consuming SIGNAL events from the Kafka topic
        await self.consume_messages(self.consume_topic, self.process_signal_event)

    async def process_signal_event(self, signal_event: Event):
        """
        Process the SIGNAL event and execute the order.

        :param signal_event: The SIGNAL event received from Kafka.

        PlaceOrder
        {
            "variety":"NORMAL",
            "tradingsymbol":"SBIN-EQ",
            "symboltoken":"3045",
            "transactiontype":"BUY",
            "exchange":"NSE",
            "ordertype":"MARKET",
            "producttype":"INTRADAY",
            "duration":"DAY",
            "price":"194.50",
            "squareoff":"0",
            "stoploss":"0",
            "quantity":"1"
        }

        ModifyOrder
        {
            "variety": "NORMAL",
            "orderid": "201020000000080",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "194.00",
            "quantity": "1"
        }

        CancelOrder
        payload = "{
            "variety": "NORMAL",
            "orderid": "201020000000080"
        }"
        """
        # Parse the JSON payload
        signal_data = json.loads(signal_event.payload)

        # Extract the message type to determine the type of request
        message_type = signal_data.get("_message_type")

        # Map the message type to the appropriate request class and function
        handler_map = {
            "PlaceOrderMessage": (PlaceOrderRequest, self.connection_manager.smartConnect.placeOrder, PlaceOrderResponse),
            "ModifyOrderRequest": (ModifyOrderRequest, self.connection_manager.smartConnect.modifyOrder, ModifyOrderResponse),
            "CancelOrderRequest": (CancelOrderRequest, self.connection_manager.smartConnect.cancelOrder, CancelOrderResponse)
        }

        if message_type in handler_map:
            request_class, method_to_invoke, response_class = handler_map[message_type]

            # Convert the signal data into the appropriate request object
            request_obj = request_class(**signal_data)

            # Invoke the corresponding method on the smartConnect object
            response_data = method_to_invoke(asdict(request_obj))

            # Construct the appropriate response object
            response_obj = response_class(
                status=True,  # This should be based on the actual response
                message="Operation completed successfully",
                errorcode="",
                data=response_class.data.__annotations__["data"](**response_data)  # Assuming the data attribute is nested
            )

            print(response_obj)
        else:
            print(f"Unknown message type: {message_type}")
