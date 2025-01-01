import json
from dataclasses import asdict

from algoLibs import Signal, MessageRouter
# from algofarm.LiveTrading.OrderManagement.OrderRequests import PlaceOrderRequest, ModifyOrderRequest, \
#     CancelOrderRequest, PlaceOrderResponse, ModifyOrderResponse, CancelOrderResponse

from algoLibs.live_trading.events.events import EventType, Event
from algoLibs.live_trading.services.core_micro_service import CoreMicroService

from algoFarmAdapter.external.smart_api_connection_manager import SmartApiConnectionManager
from algoFarmAdapter.order_management import PlaceOrderRequest, ModifyOrderRequest, CancelOrderRequest, \
    PlaceOrderResponse, ModifyOrderResponse, CancelOrderResponse

class ExecutionHandler(CoreMicroService):
    def __init__(self, service_name, kafka_bootstrap_servers, api_key, consume_topic=EventType.Signal_Event.name):
        super().__init__(service_name, kafka_bootstrap_servers,kafka_consumer_callback=self.process_signal_event,
                         consume_topics=[consume_topic])
        self.connection_manager = SmartApiConnectionManager(api_key)
        self.consume_topic = consume_topic
        self.router = MessageRouter()
        self.register_handlers()

    def register_handlers(self):
        @self.router.route("PlaceOrderMessage")
        def handle_place_order(message_data: dict):
            try:
                # Convert message data to Signal object
                signal = Signal(**message_data)
                # Convert Signal to PlaceOrderRequest
                place_order_request = self.convert_signal_to_place_order_request(signal)
                # Place the order
                response_data = self.connection_manager.smartConnect.placeOrder(asdict(place_order_request))
                # Create and process PlaceOrderResponse
                response_obj = PlaceOrderResponse(
                    status=True,  # Update based on actual response
                    message="Order placed successfully",
                    errorcode="",
                    data=response_data  # Adjust according to your actual response structure
                )
                print(response_obj)
            except Exception as e:
                print(f"Error in handle_place_order: {e}")

        @self.router.route("ModifyOrderMessage")
        def handle_modify_order(message_data: dict):
            try:
                # Convert message data to ModifyOrderRequest
                modify_order_request = ModifyOrderRequest(**message_data)
                # Modify the order
                response_data = self.connection_manager.smartConnect.modifyOrder(asdict(modify_order_request))
                # Create and process ModifyOrderResponse
                response_obj = ModifyOrderResponse(
                    status=True,  # Update based on actual response
                    message="Order modified successfully",
                    errorcode="",
                    data=response_data
                )
                print(response_obj)
            except Exception as e:
                print(f"Error in handle_modify_order: {e}")

        @self.router.route("CancelOrderMessage")
        def handle_cancel_order(message_data: dict):
            try:
                # Convert message data to CancelOrderRequest
                cancel_order_request = CancelOrderRequest(**message_data)
                # Cancel the order
                response_data = self.connection_manager.smartConnect.cancelOrder(asdict(cancel_order_request))
                # Create and process CancelOrderResponse
                response_obj = CancelOrderResponse(
                    status=True,  # Update based on actual response
                    message="Order canceled successfully",
                    errorcode="",
                    data=response_data
                )
                print(response_obj)
            except Exception as e:
                print(f"Error in handle_cancel_order: {e}")

    async def run(self):
        await self.start_kafka()
        await self.consume_messages()

    async def process_signal_event(self, signal_event: Event):
        try:
            # Parse the JSON payload
            message_data = json.loads(signal_event.payload)
            # Get the message type from the data
            message_type = message_data.get("_message_type")
            if not message_type:
                raise ValueError("Message type not found in the message data")

            # Dispatch the message to the appropriate handler
            self.router.dispatch(message_type, message_data)
        except Exception as e:
            print(f"Error in process_signal_event: {e}")

    def convert_signal_to_place_order_request(self, signal: Signal) -> PlaceOrderRequest:
        # Fetch the symbol token
        symbol_token = signal.token
        if not symbol_token:
            raise ValueError(f"Symbol token not found for {signal.trading_symbol} on {signal.exchange}")

        # Create the PlaceOrderRequest object
        place_order_request = PlaceOrderRequest(
            variety=signal.variety.upper(),
            tradingsymbol=signal.trading_symbol,
            symboltoken=symbol_token,
            transactiontype=signal.transaction_type.value,
            exchange=signal.exchange.upper(),
            ordertype=signal.ordertype.upper(),
            producttype=signal.product_type.upper(),
            duration=signal.duration.upper(),
            quantity=str(signal.quantity),
            price="0",  # Assuming market order; adjust as necessary
            squareoff="0",
            stoploss="0"
        )
        return place_order_request

    # def get_symbol_token(self, trading_symbol: str, exchange: str) -> str:
    #     # Placeholder implementation; replace with actual logic to fetch symbol token
    #     symbol_tokens = {
    #         "NSE": {"SBIN-EQ": "3045"},
    #         # Add more symbols as needed
    #     }
    #     return symbol_tokens.get(exchange.upper(), {}).get(trading_symbol.upper(), "")


# class ExecutionHandler(CoreMicroService):
#
#
#     def __init__(self, service_name, kafka_bootstrap_servers, api_key,consume_topic=EventType.Signal_Event):
#         """
#         ExecutionHandler class that extends the CoreMicroService to handle order execution.
#
#         :param service_name: Name of the microservice.
#         :param kafka_bootstrap_servers: Kafka bootstrap servers.
#         :param api_key: API key to connect to the brokerage.
#         :param sampling_frequency: Frequency in seconds for processing.
#         :param consume_topic: The Kafka topic to consume SIGNAL events from.
#         """
#         super().__init__(service_name, kafka_bootstrap_servers)
#         self.connection_manager = SmartApiConnectionManager(api_key)
#         self.consume_topic = consume_topic
#
#     async def run(self):
#         """Main loop to process SIGNAL events and execute orders."""
#         # Start consuming SIGNAL events from the Kafka topic
#         await self.consume_messages(self.consume_topic, self.process_signal_event)
#
#     async def process_signal_event(self, signal_event: Event):
#         """
#         Process the SIGNAL event and execute the order.
#
#         :param signal_event: The SIGNAL event received from Kafka.
#
#         PlaceOrder
#         {
#             "variety":"NORMAL",
#             "tradingsymbol":"SBIN-EQ",
#             "symboltoken":"3045",
#             "transactiontype":"BUY",
#             "exchange":"NSE",
#             "ordertype":"MARKET",
#             "producttype":"INTRADAY",
#             "duration":"DAY",
#             "price":"194.50",
#             "squareoff":"0",
#             "stoploss":"0",
#             "quantity":"1"
#         }
#
#         ModifyOrder
#         {
#             "variety": "NORMAL",
#             "orderid": "201020000000080",
#             "ordertype": "LIMIT",
#             "producttype": "INTRADAY",
#             "duration": "DAY",
#             "price": "194.00",
#             "quantity": "1"
#         }
#
#         CancelOrder
#         payload = "{
#             "variety": "NORMAL",
#             "orderid": "201020000000080"
#         }"
#         """
#         # Parse the JSON payload
#         signal_data = json.loads(signal_event.payload)
#
#         # Extract the message type to determine the type of request
#         message_type = signal_data.get("_message_type")
#
#         # Map the message type to the appropriate request class and function
#         handler_map = {
#             "PlaceOrderMessage": (PlaceOrderRequest, self.connection_manager.smartConnect.placeOrder, PlaceOrderResponse),
#             "ModifyOrderRequest": (ModifyOrderRequest, self.connection_manager.smartConnect.modifyOrder, ModifyOrderResponse),
#             "CancelOrderRequest": (CancelOrderRequest, self.connection_manager.smartConnect.cancelOrder, CancelOrderResponse)
#         }
#
#         if message_type in handler_map:
#             request_class, method_to_invoke, response_class = handler_map[message_type]
#
#             # Convert the signal data into the appropriate request object
#             request_obj = request_class(**signal_data)
#
#             # Invoke the corresponding method on the smartConnect object
#             response_data = method_to_invoke(asdict(request_obj))
#
#             # Construct the appropriate response object
#             response_obj = response_class(
#                 status=True,  # This should be based on the actual response
#                 message="Operation completed successfully",
#                 errorcode="",
#                 data=response_class.data.__annotations__["data"](**response_data)  # Assuming the data attribute is nested
#             )
#
#             print(response_obj)
#         else:
#             print(f"Unknown message type: {message_type}")
