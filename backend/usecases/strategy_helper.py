

from typing import Optional, Tuple
from backend.models.candleStick import CandleStickDataType
from backend.models.order import OrderDataType, OrderSideEnum
from backend.models.strategy import ExitConditionDataSourceEnum, StrategyDataType
from backend.models.trade import PnlDataType, TradeDataType, TradeDirectionTypeEnum, TradeOutputEnum, TradeStatusEnum
from datetime import datetime
import pandas as pd
import plotly.express as px


def getActiveTickers(tradeData: TradeDataType):
    orderBook = {}
    for order in tradeData.entry_orders:
        if order.ticker in orderBook.keys():
            orderBook[order.ticker] = orderBook[order.ticker] + \
                order.quantity if order.order_side == OrderSideEnum.BUY else -1 * order.quantity
        else:
            orderBook[order.ticker] = order.quantity if order.order_side == OrderSideEnum.BUY else -1 * order.quantity

    for order in tradeData.exit_orders:
        orderBook[order.ticker] = orderBook[order.ticker] - \
            order.quantity if order.order_side == OrderSideEnum.BUY else -1 * order.quantity

    activeTickers = []
    for ticker in orderBook.keys():
        if orderBook[ticker] != 0.0:
            activeTickers.append(ticker)

    return activeTickers


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
