

from typing import Tuple
from backend.model.candleStick import CandleStickDataType, CandleStickDictDataType
from backend.model.order import OrderDataType, OrderSideEnum, OrderStatusType, OrderTypeEnum
from backend.model.strategy import SpreadOrderDataType, SpreadStrikeDataType, SpreadStrikeTypeEnum, StrategyDataType
from backend.model.trade import TradeDataType
from backend.usecase.strategy_helper import getActiveTickers, getActiveTickersWithQuantity, updateProfitAndLoss
from backend.utils.strategyUtil import getLotSize, getSpreadOrderStrike


def placeEntryOrders(timestamp: int, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDataType]) -> Tuple[int, list[OrderDataType]]:
    underlyingCandle = candleStickData[strategy.ticker.upper()]
    atm_strike = getSpreadOrderStrike(
        strategy.ticker, underlyingCandle.open, SpreadStrikeDataType(strike_type=SpreadStrikeTypeEnum.ATM_AND_STRIKE_POINTS, value="ATM+0"))

    orders = []
    for order in strategy.spread.order:
        strike = getSpreadOrderStrike(
            strategy.ticker, underlyingCandle.open, order.strike)
        strikeCandle = candleStickData[str(
            strike) + order.contract_type]
        orders.append(
            placeOrder(str(strike) + order.contract_type, strikeCandle.open,
                       order.order_side, getLotSize(strategy.ticker), order.stoploss_percent, timestamp)
        )

        if order.hedge_strike != None:
            hedgeStrike = getSpreadOrderStrike(
                strategy.ticker, underlyingCandle.open, order.hedge_strike)
            hedgeStrikeCandle = candleStickData[str(
                strike) + order.contract_type]
            orders.append(
                placeOrder(str(hedgeStrike) + order.contract_type, hedgeStrikeCandle.open,
                           order.order_side.getOppositeSide(), getLotSize(strategy.ticker), order.stoploss_percent, timestamp, True)
            )

    return atm_strike, orders


def placeOrder(ticker: str, ask_price: float, side: OrderSideEnum, quantity: int, stoploss_percent: float, timestamp: int, hedge: bool = False) -> OrderDataType:
    output = OrderDataType(
        id=-1,
        ticker=ticker,
        leverage=1,
        order_type=OrderTypeEnum.MARKET,
        order_status=OrderStatusType.EXECUTED,
        order_side=side,
        quantity=quantity,
        ask_price=ask_price,
        final_price=ask_price,
        fee=1.75,
        blocked_margin=-1,
        transaction_time=timestamp,
        stoploss_percent=stoploss_percent,
        hedge_order=hedge
    )
    return output


def processExitLeg(spreadOrder: SpreadOrderDataType, tradeData: TradeDataType, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDataType]) -> TradeDataType:
    underlyingCandle = candleStickData[strategy.ticker.upper()]

    strike = getSpreadOrderStrike(
        strategy.ticker, tradeData.underlying_data[0], spreadOrder.strike)
    strikeCandle = candleStickData[str(
        strike) + spreadOrder.contract_type]
    tradeData.exit_orders.append(
        placeOrder(str(strike) + spreadOrder.contract_type, strikeCandle.open,
                   spreadOrder.order_side.getOppositeSide(), getLotSize(strategy.ticker), spreadOrder.stoploss_percent, underlyingCandle.timestamp)
    )

    if spreadOrder.hedge_strike != None:
        hedgeStrike = getSpreadOrderStrike(
            strategy.ticker, tradeData.underlying_data[0], spreadOrder.hedge_strike)
        hedgeStrikeCandle = candleStickData[str(
            strike) + spreadOrder.contract_type]
        tradeData.exit_orders.append(
            placeOrder(str(hedgeStrike) + spreadOrder.contract_type, hedgeStrikeCandle.open,
                       spreadOrder.order_side, getLotSize(strategy.ticker), spreadOrder.stoploss_percent, underlyingCandle.timestamp, True)
        )

    return tradeData


def processRemainingExitLegs(tradeData: TradeDataType, candleStickData: dict[str, CandleStickDataType]) -> TradeDataType:

    orderBook = getActiveTickersWithQuantity(tradeData)

    for ticker in orderBook.keys():
        quantity = orderBook[ticker] if orderBook[ticker] > 0 else - \
            1 * orderBook[ticker]
        order_side = OrderSideEnum.BUY if orderBook[ticker] < 0 else OrderSideEnum.SELL
        if orderBook[ticker] != 0.0:
            tradeData.exit_orders.append(
                placeOrder(ticker, candleStickData[ticker].open,
                           order_side, quantity, -1, candleStickData[ticker].timestamp)
            )

    tradeData = updateProfitAndLoss(tradeData, candleStickData)
    return tradeData
