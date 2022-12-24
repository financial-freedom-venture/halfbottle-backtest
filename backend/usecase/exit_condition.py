from datetime import datetime, timedelta
from typing import Optional
from backend.dto.exitDto import TradeExitConditionResponseDTO, TradeExitResponseDataDTO, TradeExitTypeEnum
from backend.model.candleStick import CandleStickDataType
from backend.model.strategy import SpreadStoplossConditionTypeEnum, StrategyDataType
from backend.model.trade import TradeDataType
from backend.usecase.stoploss_conditions import checkIfLegStopLossHit, checkIfMTMStopLossHit, checkIfTakeProfitHit
from backend.usecase.strategy_helper import getActiveTickers, getOrderData
from backend.utils.strategyUtil import getSpreadOrderStrike


def checkExitCondition(tradeData: TradeDataType, timestamp: int, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDataType]) -> Optional[TradeExitConditionResponseDTO]:
    output = TradeExitConditionResponseDTO(
        exit_type=TradeExitTypeEnum.NO_EXIT,
        data=None
    )

    # no need to check exit condition if no trade entered
    activeTickers = getActiveTickers(tradeData)
    if len(activeTickers) == 0:
        return output

    underlyingCandleData = candleStickData[strategy.ticker]

    if checkExitTime(timestamp, strategy):
        output.data = TradeExitResponseDataDTO(orders=strategy.spread.order)
        output.exit_type = TradeExitTypeEnum.COMPLETE_EXIT
        return output

    # exit condition when stoploss hits
    for spreadOrder in strategy.spread.order:
        tempTicker = str(getSpreadOrderStrike(
            strategy.ticker, tradeData.atm_strike, spreadOrder.strike)) + spreadOrder.contract_type
        if tempTicker not in activeTickers:
            continue
        activeCandleData = candleStickData[tempTicker]
        oppositeOrder = getOrderData(tradeData.entry_orders, tempTicker)
        if checkIfLegStopLossHit(oppositeOrder, activeCandleData):
            if strategy.spread.stoploss_condition == SpreadStoplossConditionTypeEnum.PARTIAL_EXIT:
                output.data = TradeExitResponseDataDTO(orders=[spreadOrder])
                output.exit_type = TradeExitTypeEnum.PARTIAL_EXIT
            else:
                output.data = TradeExitResponseDataDTO(
                    orders=strategy.spread.order)
                output.exit_type = TradeExitTypeEnum.COMPLETE_EXIT
            return output

    # exit condition when MTM stoploss hits
    if checkIfMTMStopLossHit(tradeData, strategy, underlyingCandleData):
        output.data = TradeExitResponseDataDTO(
            orders=strategy.spread.order)
        output.exit_type = TradeExitTypeEnum.COMPLETE_EXIT
        return output

    # # exit condition when trailing stoploss hits
    # if checkIfTrailingStopLossHit(tradeData, strategy):
    #     tradeData = processRemainingExitLegs(
    #         tradeData, candleData)

    # exit condition when take profit hits
    if checkIfTakeProfitHit(tradeData, strategy, underlyingCandleData):
        output.data = TradeExitResponseDataDTO(
            orders=strategy.spread.order)
        output.exit_type = TradeExitTypeEnum.COMPLETE_EXIT
        return output

    return output


def checkExitTime(timestamp: int, strategy: StrategyDataType) -> bool:
    currentDatetime = datetime.fromtimestamp(timestamp)

    exitDatetime = datetime(currentDatetime.year, currentDatetime.month, currentDatetime.day) + timedelta(
        hours=int(strategy.exit.time.strip().split(":")[0]),
        minutes=int(strategy.exit.time.strip().split(":")[1]),
        seconds=int(strategy.exit.time.strip().split(":")[2]) if len(
            strategy.entry.time.strip().split(":")) == 3 else 0
    )

    if currentDatetime >= exitDatetime:
        return True

    return False
