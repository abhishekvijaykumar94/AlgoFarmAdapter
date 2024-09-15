from enum import Enum

class Variety(Enum):
    NORMAL = "Normal Order (Regular)"
    STOPLOSS = "Stop loss order"
    AMO = "After Market Order"
    ROBO = "ROBO (Bracket Order)"

class TransactionType(Enum):
    BUY = "Buy"
    SELL = "Sell"

class OrderType(Enum):
    MARKET = "Market Order (MKT)"
    LIMIT = "Limit Order (L)"
    STOPLOSS_LIMIT = "Stop Loss Limit Order (SL)"
    STOPLOSS_MARKET = "Stop Loss Market Order (SL-M)"

class ProductType(Enum):
    DELIVERY = "Cash & Carry for equity (CNC)"
    CARRYFORWARD = "Normal for futures and options (NRML)"
    MARGIN = "Margin Delivery"
    INTRADAY = "Margin Intraday Squareoff (MIS)"
    BO = "Bracket Order (Only for ROBO)"

class Duration(Enum):
    DAY = "Regular Order"
    IOC = "Immediate or Cancel"

class Exchange(Enum):
    BSE = "BSE Equity"
    NSE = "NSE Equity"
    NFO = "NSE Future and Options"
    MCX = "MCX Commodity"
    BFO = "BSE Futures and Options"
    CDS = "Currency Derivate Segment"

class OrderStatus(Enum):
    AB00 = "after-successful connection"
    AB01 = "open"
    AB02 = "cancelled"
    AB03 = "rejected"
    AB04 = "modified"
    AB05 = "complete"
    AB06 = "after market order req received"
    AB07 = "cancelled after market order"
    AB08 = "modify after market order req received"
    AB09 = "open pending"
    AB10 = "trigger pending"
    AB11 = "modify pending"