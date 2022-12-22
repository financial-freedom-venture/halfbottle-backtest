from datetime import datetime, timedelta
from typing import Optional, Tuple
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.models.candleStick import CandleStickDictDataType
from backend.models.strategy import StrategyDataType
from backend.models.trade import TradeDataType, TradeOutputEnum, TradeStatusEnum
from backend.usecases.order_helper import placeEntryOrders, processRemainingExitLegs
from backend.usecases.stoploss_conditions import checkIfTakeProfitHit, processStoplossHit
from backend.usecases.strategy_helper import getActiveTickers, updateProfitAndLoss
from backend.utils.candleUtils import convertFastAccessData, getMostRecentCandle
from backend.utils.strategyUtil import getSpreadOrderStrike


def enterTrade(historicalDataService: HistoricalDataService, timestamp: int, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDictDataType]) -> Tuple[dict[str, CandleStickDictDataType], Optional[TradeDataType]]:
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
        return candleStickData, None

    # we can multithread here
    tempCandleData = {}
    for order in strategy.spread.order:
        strike = getSpreadOrderStrike(
            strategy.ticker, candleStickData[strategy.ticker].data[timestamp].open, order.strike)
        if str(strike) + order.contract_type not in tempCandleData.keys():
            strikeData = historicalDataService.getOptionsData(
                strategy.ticker, strike, strategy.expiry, order.contract_type, datetime.fromtimestamp(timestamp))
            if strikeData != None:
                tempCandleData[str(strike) + order.contract_type] = strikeData

        if order.hedge_strike != None:
            hedge_strike = getSpreadOrderStrike(
                strategy.ticker, candleStickData[strategy.ticker].data[timestamp].open, order.hedge_strike)
            if str(hedge_strike) + order.contract_type not in tempCandleData.keys():
                hedge_strikeData = historicalDataService.getOptionsData(
                    strategy.ticker, hedge_strike, strategy.expiry, order.contract_type, datetime.fromtimestamp(timestamp))
                if hedge_strikeData != None:
                    tempCandleData[str(hedge_strike) +
                                   order.contract_type] = hedge_strikeData

    candleStickData = candleStickData | convertFastAccessData(tempCandleData)

    atm_strike, orders = placeEntryOrders(timestamp, strategy, candleStickData)
    output = TradeDataType(
        leverage=1,
        spread=[],
        quantity=1,
        atm_strike=atm_strike,
        entry_time=timestamp,
        exit_time=-1,
        spread_name=strategy.spread.spread_name,
        entry_price=-1,
        exit_price=-1,
        status=TradeStatusEnum.ENTERED,
        trading_fee=-1,
        pnl=[],
        take_profit=-1,
        stop_loss=-1,
        trade_output=TradeOutputEnum.IN_PROGRESS,
        entry_orders=orders,
        exit_orders=[],
        underlying_data=[
            candleStickData[strategy.ticker.upper()].data[timestamp].open]
    )
    return candleStickData, output


def exitTrade(tradeData: TradeDataType, timestamp: int, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDictDataType]) -> Optional[TradeDataType]:
    currentDatetime = datetime.fromtimestamp(timestamp)

    candleData = candleStickData[strategy.ticker.upper()].data[timestamp]
    tradeData.underlying_data.append(candleData.open)

    activeTickers = getActiveTickers(tradeData)
    if len(activeTickers) == 0:
        # update other things also in trade data
        tradeData.status = TradeStatusEnum.EXITED
        return tradeData

    optionsCandleData = getMostRecentCandle(
        activeTickers, timestamp, candleStickData)

    exitDatetime = datetime(currentDatetime.year, currentDatetime.month, currentDatetime.day) + timedelta(
        hours=int(strategy.exit.time.strip().split(":")[0]),
        minutes=int(strategy.exit.time.strip().split(":")[1]),
        seconds=int(strategy.exit.time.strip().split(":")[2]) if len(
            strategy.entry.time.strip().split(":")) == 3 else 0
    )

    # exit condition if current time exceeds max time
    candleDatetime = datetime.fromtimestamp(candleData.timestamp)
    if candleDatetime >= exitDatetime:
        tradeData = processRemainingExitLegs(
            tradeData, optionsCandleData)
        return tradeData

    # exit condition when stoploss hist
    tradeData = processStoplossHit(tradeData, strategy, optionsCandleData)

    # exit condition when take profit hits
    if checkIfTakeProfitHit(tradeData, strategy, candleData):
        tradeData = processRemainingExitLegs(
            tradeData, optionsCandleData)
        return tradeData

    tradeData = updateProfitAndLoss(tradeData, optionsCandleData)

    return tradeData
