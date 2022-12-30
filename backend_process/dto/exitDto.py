from enum import Enum
from typing import Optional, Union
from backend_process.model.baseModel import CustomBaseModel
from backend_process.model.order import OrderDataType, OrderSideEnum
from backend_process.model.strategy import SpreadOrderDataType


class TradeExitTypeEnum(str, Enum):
    COMPLETE_EXIT = "complete_exit"
    PARTIAL_EXIT = "exit_one_leg"
    NO_EXIT = "no_exit"


class TradeExitResponseDataDTO(CustomBaseModel):
    orders: list[SpreadOrderDataType] = []


class TradeExitConditionResponseDTO(CustomBaseModel):
    exit_type: TradeExitTypeEnum
    data: Optional[TradeExitResponseDataDTO]
