
from backend_process.model.candleStick import CandleStickDataType
from backend_process.model.order import OrderDataType, OrderSideEnum
from backend_process.model.strategy import ExitConditionDataSourceEnum, StrategyDataType
from backend_process.model.trade import TradeDataType, TradeDirectionTypeEnum


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
