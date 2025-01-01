from dataclasses import dataclass
from typing import Optional


@dataclass
class SignalPayload:
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