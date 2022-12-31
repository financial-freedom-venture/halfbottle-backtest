from enum import Enum
from typing import Optional, Union
from model.baseModel import CustomBaseModel
from model.order import OrderDataType, OrderSideEnum
from model.strategy import SpreadOrderDataType


class TradeEntryTypeEnum(str, Enum):
    PARTIAL_ENTRY = "partial_entry"
    COMPLETE_ENTRY = "complete_entry"
    NO_ENTRY = "no_entry"
    ADJUSTMENT = "adjustment"


class TradeEntryResponseDataDTO(CustomBaseModel):
    orders: list[SpreadOrderDataType] = []


class TradeEntryConditionResponseDTO(CustomBaseModel):
    entry_type: TradeEntryTypeEnum
    data: Optional[TradeEntryResponseDataDTO]
