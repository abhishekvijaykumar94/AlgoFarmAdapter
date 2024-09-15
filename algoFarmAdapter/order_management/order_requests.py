
from dataclasses import dataclass
from typing import Optional


class smartApiOrderDataClass():

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

# """
#        Class representing an order to be placed.
#
#        Attributes:
#        ----------
#        tradingsymbol : str
#            Trading Symbol of the instrument.
#        symboltoken : str
#            Symbol Token is a unique identifier.
#        exchange : str
#            Name of the exchange.
#        transactiontype : str
#            Transaction type, either BUY or SELL.
#        ordertype : str
#            Order type (e.g., MARKET, LIMIT).
#        quantity : int
#            Quantity to transact.
#        producttype : str
#            Product type (e.g., CNC, MIS).
#        price : float, optional
#            The min or max price to execute the order at (for LIMIT orders).
#        triggerprice : float, optional
#            The price at which an order should be triggered (for SL, SL-M orders).
#        squareoff : float, optional
#            Only for ROBO (Bracket Order).
#        stoploss : float, optional
#            Only for ROBO (Bracket Order).
#        trailingStopLoss : float, optional
#            Only for ROBO (Bracket Order).
#        disclosedquantity : int, optional
#            Quantity to disclose publicly (for equity trades).
#        duration : str
#            Order duration (e.g., DAY, IOC).
#        ordertag : str, optional
#            An optional tag to apply to an order to identify it.
#        """
@dataclass
class PlaceOrderRequest(smartApiOrderDataClass):

    _message_type="PlaceOrderMessage"
    variety: str
    tradingsymbol: str
    symboltoken: str
    transactiontype: str
    exchange: str
    ordertype: str
    producttype: str
    duration: str
    quantity: str
    price: Optional[str] = None
    squareoff: str = "0"
    stoploss: str = "0"

@dataclass
class PlaceOrderResponseData(smartApiOrderDataClass):
    script: str
    orderid: str
    uniqueorderid: str

@dataclass
class PlaceOrderResponse(smartApiOrderDataClass):
    status: bool
    message: str
    errorcode: str
    data: PlaceOrderResponseData

@dataclass
class ModifyOrderRequest(smartApiOrderDataClass):
    _message_type = "ModifyOrderRequest"
    variety: str
    orderid: str
    ordertype: str
    producttype: str
    duration: str
    price: str
    quantity: str
    tradingsymbol: str
    symboltoken: str
    exchange: str

@dataclass
class ModifyOrderResponseData(smartApiOrderDataClass):
    orderid: str
    uniqueorderid: str

@dataclass
class ModifyOrderResponse(smartApiOrderDataClass):
    status: bool
    message: str
    errorcode: str
    data: ModifyOrderResponseData

@dataclass
class CancelOrderRequest(smartApiOrderDataClass):
    _message_type = "CancelOrderRequest"
    variety: str
    orderid: str

@dataclass
class CancelOrderResponseData(smartApiOrderDataClass):
    orderid: str
    uniqueorderid: str

@dataclass
class CancelOrderResponse(smartApiOrderDataClass):
    status: bool
    message: str
    errorcode: str
    data: CancelOrderResponseData

@dataclass
class OrderData:
    variety: str
    ordertype: str
    ordertag: str
    producttype: str
    price: float
    triggerprice: float
    quantity: str
    disclosedquantity: str
    duration: str
    squareoff: float
    stoploss: float
    trailingstoploss: float
    tradingsymbol: str
    transactiontype: str
    exchange: str
    symboltoken: str
    instrumenttype: Optional[str]
    strikeprice: float
    optiontype: Optional[str]
    expirydate: Optional[str]
    lotsize: str
    cancelsize: str
    averageprice: float
    filledshares: str
    unfilledshares: str
    orderid: str
    text: Optional[str]
    status: str
    orderstatus: str
    updatetime: str
    exchtime: Optional[str]
    exchorderupdatetime: Optional[str]
    fillid: Optional[str]
    filltime: Optional[str]
    parentorderid: Optional[str]
    packageid: Optional[str] #TODO Figure out how to populate strategy ID
    uniqueorderid: str

@dataclass
class OrderResponse(smartApiOrderDataClass):
    user_id: str
    status_code: str
    order_status: str
    error_message: Optional[str]
    orderData: OrderData


if __name__=="__main__":
    # Example JSON string
    json_str = '''{
        "user-id": "Your_client_code",
        "status-code": "200",
        "order-status": "AB03",
        "error-message": "",
        "orderData": {
            "variety": "NORMAL",
            "ordertype": "LIMIT",
            "ordertag": "10007712",
            "producttype": "DELIVERY",
            "price": 551,
            "triggerprice": 0,
            "quantity": "1",
            "disclosedquantity": "0",
            "duration": "DAY",
            "squareoff": 0,
            "stoploss": 0,
            "trailingstoploss": 0,
            "tradingsymbol": "SBIN-EQ",
            "transactiontype": "BUY",
            "exchange": "NSE",
            "symboltoken": "3045",
            "instrumenttype": "",
            "strikeprice": -1,
            "optiontype": "",
            "expirydate": "",
            "lotsize": "1",
            "cancelsize": "0",
            "averageprice": 0,
            "filledshares": "0",
            "unfilledshares": "1",
            "orderid": "111111111111111",
            "text": "Adapter is Logged Off",
            "status": "rejected",
            "orderstatus": "rejected",
            "updatetime": "25-Oct-2023 23:53:21",
            "exchtime": "",
            "exchorderupdatetime": "",
            "fillid": "",
            "filltime": "",
            "parentorderid": ""
        }
    }'''

    # Parse JSON and create OrderResponse object
    import json

    data = json.loads(json_str)
    order_data = OrderData(**data["orderData"])
    order_response = OrderResponse(
        user_id=data["user-id"],
        status_code=data["status-code"],
        order_status=data["order-status"],
        error_message=data.get("error-message"),
        orderData=order_data
    )

    print(order_response)