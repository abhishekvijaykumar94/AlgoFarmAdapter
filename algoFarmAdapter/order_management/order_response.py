import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

from algoFarmAdapter.order_management.order_requests import smartApiOrderDataClass, Order


@dataclass
class OrderResponse(smartApiOrderDataClass):
    user_id: str
    status_code: str
    order_status: str
    error_message: Optional[str]
    orderData: 'Order'

    def __repr__(self):
        return (f"OrderResponse(user_id={self.user_id}, status_code={self.status_code},"
                f" order_status={self.order_status},error_message={self.error_message} data={self.orderData})")

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> "OrderResponse":
        """Creates an OrderResponse instance from a JSON dictionary."""
        return OrderResponse(
            user_id=json_data["user_id"],
            status_code=json_data["status_code"],
            order_status=json_data["order_status"],
            error_message=json_data.get("error_message", ""),
            orderData=Order(**json_data["orderData"], id=None, strategy="", packageid=None, uniqueorderid=None)
        )


