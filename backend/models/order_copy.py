from enum import Enum
from typing import Optional
from backend.models.baseModel import CustomBaseModel


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
    order_id: str
    exchange_order_id: str
    exchange_code: str
    stock_code: str
    product_type: str
    action: str
    order_type: str
    stoploss: str
    quantity: str
    price: str
    validity: str
    disclosed_quantity: str
    expiry_date: str
    right: Optional[str] = None
    strike_price: int
    average_price: str
    cancelled_quantity: str
    pending_quantity: str
    status: str
    user_remark: str
    order_datetime: str
    parent_order_id: Optional[str] = None
    modification_number: Optional[int] = None
    exchange_acknowledgement_date: Optional[str] = None
    SLTP_price: Optional[str] = None
    exchange_acknowledge_number: Optional[int] = None
    initial_limit: Optional[str] = None
    intial_sltp: Optional[str] = None
    LTP: Optional[str] = None,
    limit_offset: Optional[str] = None,
    mbc_flag: Optional[str] = None,
    cutoff_price: Optional[str] = None


class OrderRequestDataType(CustomBaseModel):
    stock_code: str
    exchange_code: str
    product: str
    action: str
    order_type: str
    quantity: str
    stoploss: str = "0"
    price: str = ""
    validity: str = ""
    validity_date: str = ""
    disclosed_quantity = "0"
    expiry_date: str = ""
    right: str = ""
    strike_price: str = ""
    user_remark: str
