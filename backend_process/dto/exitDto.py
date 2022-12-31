from enum import Enum
from typing import Optional, Union
from model.baseModel import CustomBaseModel
from model.order import OrderDataType, OrderSideEnum
from model.strategy import SpreadOrderDataType


class TradeExitTypeEnum(str, Enum):
    COMPLETE_EXIT = "complete_exit"
    PARTIAL_EXIT = "exit_one_leg"
    NO_EXIT = "no_exit"


class TradeExitResponseDataDTO(CustomBaseModel):
    orders: list[SpreadOrderDataType] = []


class TradeExitConditionResponseDTO(CustomBaseModel):
    exit_type: TradeExitTypeEnum
    data: Optional[TradeExitResponseDataDTO]
