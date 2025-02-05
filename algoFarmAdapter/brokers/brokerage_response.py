from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Breakup:
    name: str
    amount: float
    msg: str
    breakup: List["Breakup"] = field(default_factory=list)

@dataclass
class Summary:
    total_charges: float
    trade_value: float
    breakup: List[Breakup]

@dataclass
class Charge:
    total_charges: float
    trade_value: float
    breakup: List[Breakup]

@dataclass
class SmartApiFees(Fees):
    summary: Summary
    charges: List[Charge]

@dataclass
class BrokerageResponse:
    status: bool
    message: str
    errorcode: str
    data: Data


