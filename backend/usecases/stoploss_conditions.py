
from backend.models.candleStick import CandleStickDataType
from backend.models.order import OrderDataType, OrderSideEnum
from backend.models.strategy import ExitConditionDataSourceEnum, SpreadStoplossConditionTypeEnum, StrategyDataType
from backend.models.trade import TradeDataType, TradeDirectionTypeEnum
from backend.usecases.order_helper import processExitLeg, processRemainingExitLegs
from backend.usecases.strategy_helper import getActiveTickers, getOrderData
from backend.usecases.trailing import checkIfTrailingStopLossHit
from backend.utils.strategyUtil import getSpreadOrderStrike


def processStoplossHit(tradeData: TradeDataType, strategy: StrategyDataType, candleData: dict[str, CandleStickDataType]) -> TradeDataType:
    activeTickers = getActiveTickers(tradeData)

    # exit condition when stoploss hits
    for spreadOrder in strategy.spread.order:
        tempTicker = str(getSpreadOrderStrike(
            strategy.ticker, tradeData.atm_strike, spreadOrder.strike)) + spreadOrder.contract_type
        if tempTicker not in activeTickers:
            continue
        activeCandleData = candleData[tempTicker]
        oppositeOrder = getOrderData(tradeData.entry_orders, tempTicker)
        if checkIfLegStopLossHit(oppositeOrder, activeCandleData):
            if strategy.spread.stoploss_condition == SpreadStoplossConditionTypeEnum.EXIT_ONE_LEG:
                tradeData = processExitLeg(
                    tempTicker, tradeData, candleData, strategy)
            else:
                tradeData = processRemainingExitLegs(
                    tradeData, candleData)
            tradeData.stoploss_hit_strikes[tempTicker] = activeCandleData.open

    # exit condition when MTM stoploss hits
    if checkIfMTMStopLossHit(tradeData, strategy, candleData):
        tradeData = processRemainingExitLegs(
            tradeData, candleData)

    # exit condition when trailing stoploss hits
    if checkIfTrailingStopLossHit(tradeData, strategy):
        tradeData = processRemainingExitLegs(
            tradeData, candleData)

    return tradeData


def checkIfLegStopLossHit(order: OrderDataType, currentCandle: CandleStickDataType) -> bool:
    if order.stoploss_percent <= 0:
        return False
    if order.order_side == OrderSideEnum.BUY:
        finalPrice = order.final_price - order.final_price*order.stoploss_percent/100
        if currentCandle.open < finalPrice:
            return True
        else:
            return False
    else:
        finalPrice = order.final_price + order.final_price*order.stoploss_percent/100
        if currentCandle.open > finalPrice:
            return True
        else:
            return False


def checkIfTakeProfitHit(tradeData: TradeDataType, strategy: StrategyDataType, candleData: CandleStickDataType) -> bool:
    if strategy.exit.take_profit <= 0:
        return False

    if strategy.exit.data_source == ExitConditionDataSourceEnum.UNDERLYING_POINTS:
        underlying_points = tradeData.underlying_data[len(
            tradeData.underlying_data) - 1] - tradeData.underlying_data[0]

        if strategy.exit.direction == TradeDirectionTypeEnum.SHORT:
            underlying_points = -1*underlying_points

        if underlying_points < 0:
            return False
        if underlying_points >= strategy.exit.take_profit:
            return True
    else:
        if tradeData.pnl[len(tradeData.pnl) - 1].points >= strategy.exit.take_profit:
            return True

    return False


def checkIfMTMStopLossHit(tradeData: TradeDataType, strategy: StrategyDataType, candleData: CandleStickDataType) -> bool:
    if strategy.exit.stoploss <= 0:
        return False

    if strategy.exit.data_source == ExitConditionDataSourceEnum.UNDERLYING_POINTS:
        underlying_points = tradeData.underlying_data[len(
            tradeData.underlying_data) - 1] - tradeData.underlying_data[0]

        if strategy.exit.direction == TradeDirectionTypeEnum.SHORT:
            underlying_points = -1*underlying_points

        if underlying_points > 0:
            return False
        if -1*underlying_points >= strategy.exit.stoploss:
            return True
    else:
        if tradeData.pnl[len(tradeData.pnl)-1].points > 0:
            return False
        if -1 * tradeData.pnl[len(tradeData.pnl)-1].points >= strategy.exit.stoploss:
            return True
