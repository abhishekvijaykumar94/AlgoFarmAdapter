import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

from algoFarmAdapter.order_management.order_constants import OrderStatus



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
    _message_type: str = "PlaceOrderMessage"
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

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> "PlaceOrderResponse":
        """Creates a PlaceOrderResponse instance from a JSON dictionary."""
        return PlaceOrderResponse(
            status=json_data["status"],
            message=json_data["message"],
            errorcode=json_data["errorcode"],
            data=PlaceOrderResponseData(**json_data["data"])
        )


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
class Order:

    orderid: str
    variety: str
    ordertype: str
    producttype: str
    price: float
    quantity: str
    duration: str
    squareoff: float
    stoploss: float
    tradingsymbol: str
    transactiontype: str
    exchange: str
    symboltoken: str
    strategy: str
    id: Optional[int] = None
    ordertag: Optional[str] = None
    triggerprice: Optional[float] = None
    disclosedquantity: Optional[str] = None
    trailingstoploss: Optional[float] = None
    instrumenttype: Optional[str] = None
    strikeprice: Optional[float]= None
    optiontype: Optional[str]= None
    expirydate: Optional[str]= None
    lotsize: Optional[str]= None
    cancelsize: Optional[str]= None
    averageprice: Optional[str]= None
    filledshares: Optional[str]= None
    unfilledshares: Optional[str]= None
    text: Optional[str]= None
    status: Optional[str]= None
    orderstatus: Optional[str]= None
    updatetime: Optional[str]= None
    exchtime: Optional[str]= None
    exchorderupdatetime: Optional[str]= None
    fillid: Optional[str]= None
    filltime: Optional[str]= None
    parentorderid: Optional[str]= None
    packageid: Optional[str] = None#TODO Figure out how to populate strategy ID
    uniqueorderid: Optional[str]= None


    def update_order_response(self,order_response:'OrderResponse'):

        if order_response.order_status == OrderStatus.AB05:

            self.orderstatus = order_response.order_status
            self.filledshares = order_response.orderData.filledshares
            self.unfilledshares = order_response.orderData.unfilledshares
            self.averageprice = order_response.orderData.averageprice
            self.exchorderupdatetime = order_response.orderData.exchorderupdatetime

        elif order_response.order_status == OrderStatus.AB02 or order_response.order_status == OrderStatus.AB03:

            self.orderstatus = order_response.order_status
            self.exchorderupdatetime = order_response.orderData.exchorderupdatetime






