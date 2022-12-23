from enum import Enum
from typing import Union
from backend.model.baseModel import CustomBaseModel
from backend.model.order import OrderDataType, OrderSideEnum


class TradeSpreadEntryDataType(CustomBaseModel):
    ticker: str
    side: OrderSideEnum


class TradeDirectionTypeEnum(str, Enum):
    LONG = "long"
    SHORT = "short"


class TradeStatusEnum(str, Enum):
    SEARCHING = "searching"
    ENTERED = "entered"
    PARTIAL_EXIT = "partial_exit"
    EXITED = "exited"


class TradeOutputEnum(str, Enum):
    WINNER = "winner"
    LOSER = "loser"
    IN_PROGRESS = "in_progress"


class PnlDataType(CustomBaseModel):
    time: int
    points: float


class TradeDataType(CustomBaseModel):
    leverage: int
    spread: list[TradeSpreadEntryDataType]
    quantity: int
    atm_strike: int
    entry_time: int
    exit_time: int
    spread_name: str
    entry_price: float
    exit_price: float
    status: TradeStatusEnum
    trading_fee: float
    underlying_data: list[float] = []
    pnl: list[PnlDataType]
    take_profit: float
    stop_loss: float
    trade_output: TradeOutputEnum
    entry_orders: list[OrderDataType]
    exit_orders: list[OrderDataType]
    stoploss_hit_strikes: dict[str, float] = {}


class TradeReportDataType(CustomBaseModel):
    total_points_captured: float
    total_trades: int
    total_won_points: float
    total_won_trades: int
    max_won_point: int
    total_lost_points: float
    total_lost_trades: int
    max_lost_point: int
