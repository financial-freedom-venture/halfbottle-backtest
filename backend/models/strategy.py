from enum import Enum
from typing import Optional, Union
from backend.models.baseModel import CustomBaseModel
from backend.models.candleStick import ContractTypeEnum, ExpiryTypeEnum
from backend.models.order import OrderSideEnum
from backend.models.trade import TradeDirectionTypeEnum
from backend.models.trailing import TrailingStopLossDataType


class DaysInWeekTypeEnum(str, Enum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'


class ExitConditionDataSourceEnum(str, Enum):
    UNDERLYING_POINTS = "underlying_points"
    PNL_POINTS = "pnl_points"


class SpreadStrikeTypeEnum(str, Enum):
    ATM_AND_STRIKE_POINTS = "ATM_AND_STRIKE_POINTS"


class SpreadStrikeDataType(CustomBaseModel):
    strike_type: SpreadStrikeTypeEnum
    value: Union[str, float]


class SpreadOrderDataType(CustomBaseModel):
    # currently strike = ATM+0
    strike: SpreadStrikeDataType
    order_side: OrderSideEnum
    contract_type: ContractTypeEnum
    stoploss_percent: float = -1
    hedge_strike: Optional[SpreadStrikeDataType] = None


class SpreadStoplossConditionTypeEnum(str, Enum):
    EXIT_ALL_LEG = "exit_all_leg"
    EXIT_ONE_LEG = "exit_one_leg"


class SpreadDataType(CustomBaseModel):
    spread_name: str = ""
    stoploss_condition: SpreadStoplossConditionTypeEnum = SpreadStoplossConditionTypeEnum.EXIT_ONE_LEG
    order: list[SpreadOrderDataType]


class StrategyEntryDataType(CustomBaseModel):
    included_days: list[DaysInWeekTypeEnum] = [
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    time: str


class StrategyExitDataType(CustomBaseModel):
    data_source: ExitConditionDataSourceEnum = ExitConditionDataSourceEnum.PNL_POINTS
    direction: Optional[TradeDirectionTypeEnum] = None
    trailing_stoploss: Optional[TrailingStopLossDataType] = None
    take_profit: float = -1
    stoploss: float = -1
    time: str


class StrategyDataType(CustomBaseModel):
    ticker: str
    expiry: ExpiryTypeEnum
    spread: SpreadDataType
    entry: StrategyEntryDataType
    exit: StrategyExitDataType
