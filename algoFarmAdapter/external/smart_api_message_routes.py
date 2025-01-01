from dataclasses import asdict

from algoLibs import Signal, MessageRouter

from algoFarmAdapter import PlaceOrderResponse, ModifyOrderRequest, ModifyOrderResponse, CancelOrderRequest, \
    CancelOrderResponse


class SmartApiMessageRoutes:

    def __init__(self):
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