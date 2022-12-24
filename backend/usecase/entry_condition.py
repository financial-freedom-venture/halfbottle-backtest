from datetime import datetime, timedelta
from typing import Optional
from backend.dto.entryDto import TradeEntryConditionResponseDTO, TradeEntryResponseDataDTO, TradeEntryTypeEnum
from backend.model.candleStick import CandleStickDataType
from backend.model.strategy import SpreadStrikeDataType, SpreadStrikeTypeEnum, StrategyDataType
from backend.model.trade import TradeDataType
from backend.utils.strategyUtil import getSpreadOrderStrike


def checkEntryCondition(tradeData: Optional[TradeDataType], timestamp: int, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDataType]) -> TradeEntryConditionResponseDTO:
    output = TradeEntryConditionResponseDTO(
        entry_type=TradeEntryTypeEnum.NO_ENTRY,
        data=None
    )

    # check if already entered in trade
    # this section can be extended to include adjustments
    if tradeData != None:
        return output

    if not checkEntryTime(timestamp, strategy):
        return output

    underlyingCandle = candleStickData[strategy.ticker]

    atm_strike = getSpreadOrderStrike(
        strategy.ticker, underlyingCandle.open, SpreadStrikeDataType(strike_type=SpreadStrikeTypeEnum.ATM_AND_STRIKE_POINTS, value="ATM+0"))

    output.entry_type = TradeEntryTypeEnum.COMPLETE_ENTRY
    output.data = TradeEntryResponseDataDTO(atm_strike=atm_strike)

    return output


def checkEntryTime(timestamp: int, strategy: StrategyDataType) -> bool:
    currentDatetime = datetime.fromtimestamp(timestamp)
    # filter data before entry time (adjusted for GMT)
    entryDatetime = datetime(currentDatetime.year, currentDatetime.month, currentDatetime.day) + timedelta(
        hours=int(strategy.entry.time.strip().split(":")[0]),
        minutes=int(strategy.entry.time.strip().split(":")[1]),
        seconds=int(strategy.entry.time.strip().split(":")[2]) if len(
            strategy.entry.time.strip().split(":")) == 3 else 0
    )
    exitDatetime = datetime(currentDatetime.year, currentDatetime.month, currentDatetime.day) + timedelta(
        hours=int(strategy.exit.time.strip().split(":")[0]),
        minutes=int(strategy.exit.time.strip().split(":")[1]),
        seconds=int(strategy.exit.time.strip().split(":")[2]) if len(
            strategy.entry.time.strip().split(":")) == 3 else 0
    )
    if entryDatetime > currentDatetime or currentDatetime > exitDatetime:
        return False

    return True
