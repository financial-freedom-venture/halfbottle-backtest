

from typing import Optional
from backend.models.candleStick import CandleStickDataType
from backend.models.order import OrderDataType, OrderSideEnum, OrderStatusType, OrderTypeEnum
from backend.models.strategy import ExitConditionDataSourceEnum, StrategyDataType
from backend.models.trade import PnlDataType, TradeDataType, TradeDirectionTypeEnum, TradeOutputEnum, TradeStatusEnum
from datetime import datetime
import pandas as pd
import plotly.express as px


def getAtmStrike(price: float, ticker: str) -> int:
    step = 50
    if ticker.strip().lower() == "nifty":
        step = 50
    elif ticker.strip().lower() == "banknifty":
        step = 100

    if price % step > step/2:
        return int(int(price)/step)*step + step
    else:
        return int(int(price)/step)*step


def placeOrder(ticker: str, optionsData: dict[str, CandleStickDataType], side: str, stoploss_percent: float) -> OrderDataType:
    candleData = optionsData[ticker]
    output = OrderDataType(
        id=-1,
        ticker=ticker,
        leverage=1,
        order_type=OrderTypeEnum.MARKET,
        order_status=OrderStatusType.EXECUTED,
        order_side=side,
        quantity=1,
        ask_price=candleData.open,
        final_price=candleData.open,
        fee=3.5,
        blocked_margin=-1,
        transaction_time=candleData.timestamp,
        stoploss_percent=stoploss_percent
    )
    return output


def getActiveTickers(tradeData: TradeDataType):
    entryTickers = [order.ticker for order in tradeData.entry_orders]
    exitTickers = [order.ticker for order in tradeData.exit_orders]

    return list(set(entryTickers) - set(exitTickers))


def getAllTickers(tradeData: TradeDataType):
    entryTickers = [order.ticker for order in tradeData.entry_orders]

    return list(set(entryTickers))


def getOppositeOrderSide(entry_orders: list[OrderDataType], ticker: str):
    orderSide = OrderSideEnum.INVALID

    for entry_order in entry_orders:
        if entry_order.ticker == ticker:
            orderSide = entry_order.order_side
            return orderSide.getOppositeSide()

    return orderSide


def updateProfitAndLoss(tradeData: TradeDataType, optionsCandleData: dict[str, CandleStickDataType]) -> TradeDataType:
    totalBuyPrice = 0.0
    totalSellPrice = 0.0

    pnlTimestamp = [entry.time for entry in tradeData.pnl]

    if len(tradeData.entry_orders) == len(tradeData.exit_orders):
        timestamp = 0
        for order in tradeData.entry_orders + tradeData.exit_orders:
            timestamp = optionsCandleData[order.ticker].timestamp
            if order.order_side == OrderSideEnum.BUY:
                totalBuyPrice = totalBuyPrice + order.final_price
            if order.order_side == OrderSideEnum.SELL:
                totalSellPrice = totalSellPrice + order.final_price

        tradeData.trade_output = TradeOutputEnum.WINNER if totalSellPrice - \
            totalBuyPrice > 0 else TradeOutputEnum.LOSER
        tradeData.status = TradeStatusEnum.EXITED

        pnl = PnlDataType(
            time=timestamp,
            points=totalSellPrice - totalBuyPrice
        )
        if timestamp not in pnlTimestamp:
            tradeData.pnl.append(pnl)
    else:
        activeTickers = getActiveTickers(tradeData)
        timestamp = 0

        for order in tradeData.entry_orders:
            timestamp = optionsCandleData[order.ticker].timestamp
            if order.ticker in activeTickers:
                if order.order_side == OrderSideEnum.BUY:
                    totalSellPrice = totalSellPrice + \
                        optionsCandleData[order.ticker].open
                if order.order_side == OrderSideEnum.SELL:
                    totalBuyPrice = totalBuyPrice + \
                        optionsCandleData[order.ticker].open

            if order.order_side == OrderSideEnum.BUY:
                totalBuyPrice = totalBuyPrice + order.final_price
            if order.order_side == OrderSideEnum.SELL:
                totalSellPrice = totalSellPrice + order.final_price

        for order in tradeData.exit_orders:
            timestamp = optionsCandleData[order.ticker].timestamp
            if order.order_side == OrderSideEnum.BUY:
                totalBuyPrice = totalBuyPrice + order.final_price
            if order.order_side == OrderSideEnum.SELL:
                totalSellPrice = totalSellPrice + order.final_price

            if order.transaction_time > tradeData.exit_time:
                tradeData.exit_time = order.transaction_time

        pnl = PnlDataType(
            time=timestamp,
            points=totalSellPrice - totalBuyPrice
        )
        if timestamp not in pnlTimestamp:
            tradeData.pnl.append(pnl)

    return tradeData


def getOrderData(orders: list[OrderDataType], ticker: str) -> Optional[OrderDataType]:
    for order in orders:
        if ticker.lower() == order.ticker.lower():
            return order

    return None


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


def getTickerName(ticker: str, atm: int, strike: str, contract_type: str):
    if strike.strip() == "ATM":
        strike = 0
    else:
        strike = int(strike.removeprefix("ATM"))

    tempTicker = ticker.lower() + "wk" + \
        str(atm+strike) + contract_type.lower()

    return tempTicker


def plotPnlGraph(tradeData: TradeDataType):
    data = [
        [
            str(datetime.fromtimestamp(entry.time).hour) +
            ":" + str(datetime.fromtimestamp(entry.time).minute),
            entry.points
        ] for entry in tradeData.pnl]

    # Create the pandas DataFrame
    df = pd.DataFrame(data, columns=['time', 'Profit and Loss'])
    fig = px.line(df, x="time", y="Profit and Loss",
                  title='Profit and Loss in Complete Trade')

    fig.show()
    return
