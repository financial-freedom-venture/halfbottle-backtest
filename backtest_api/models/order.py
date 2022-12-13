from typing import Optional
from enum import Enum
from backtest_api.models.baseModel import CustomBaseModel


class OrderSideEnum(str, Enum):
    BUY = "buy"
    SELL = "sell"
    INVALID = "invalid"


class OrderTypeEnum(str, Enum):
    LIMIT = "limit"
    MARKET = "market"
    INVALID = "invalid"


class OrderStatusType(str, Enum):
    OPEN = "open"
    EXECUTED = "executed"
    CANCELED = "canceled"


class OrderDataType(CustomBaseModel):
    id: str
    ticker: str
    leverage: int
    order_type: OrderTypeEnum
    order_status: OrderStatusType
    order_side: OrderSideEnum
    stoploss_percent: float
    quantity: float
    ask_price: float
    final_price: float
    fee: float
    blocked_margin: float
    transaction_time: int


class OrderSideEnum(str, Enum):
    BUY = "buy"
    SELL = "sell"
    INVALID = "invalid"

    def getOppositeSide(self):
        if self.value == self.BUY:
            return self.SELL
        if self.value == self.SELL:
            return self.BUY
        return self.INVALID


class OrderTypeEnum(str, Enum):
    LIMIT = "limit"
    MARKET = "market"
    INVALID = "invalid"


class OrderStatusType(str, Enum):
    OPEN = "open"
    EXECUTED = "executed"
    CANCELED = "canceled"


class OrderDataType(CustomBaseModel):
    id: str
    ticker: str
    leverage: int
    order_type: OrderTypeEnum
    order_status: OrderStatusType
    order_side: OrderSideEnum
    stoploss_percent: float
    quantity: float
    ask_price: float
    final_price: float
    fee: float
    blocked_margin: float
    transaction_time: int
