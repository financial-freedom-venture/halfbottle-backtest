from datetime import datetime, timedelta
import json
from typing import Optional
from backtest_api.dataservice.options_dataservice import OptionsDataService
from backtest_api.models.candleStick import CandleStickDataType
import multiprocessing
from backtest_api.models.strategy import SpreadStoplossConditionTypeEnum, StrategyDataType
from backtest_api.usecases.strategy_helper import checkIfLegStopLossHit, checkIfMTMStopLossHit, checkIfTakeProfitHit, getActiveTickers, getAllTickers, getAtmStrike, getOppositeOrderSide, getOrderData, getTickerName, placeOrder, updateProfitAndLoss
from backtest_api.models.trade import TradeDataType, TradeOutputEnum, TradeReportDataType, TradeStatusEnum
from backtest_api.usecases.trailing import checkIfTrailingStopLossHit
from time import time


DATA_PATH = "./strategy/"


class StrategyBackTester:

    def __init__(self, optionsDataService: OptionsDataService) -> None:
        self.optionsDataService = optionsDataService
        return

    def loadStrategy(self, filename) -> Optional[StrategyDataType]:
        jsonData = json.load(open(DATA_PATH + filename))

        try:
            strategyData = StrategyDataType(**jsonData)
            return strategyData
        except Exception as e:
            return None

    def longtermBacktester(self, strategy: StrategyDataType, start_date: datetime, end_date: datetime) -> TradeReportDataType:
        tradesData = []
        currentDate = start_date
        while currentDate <= end_date:
            trade = self.testStrategy(currentDate, strategy)
            if trade != None:
                tradesData.append(trade)
            currentDate = currentDate + timedelta(days=1)

        tradeReport = self.generateTradeReport(tradesData)
        return tradeReport

    def longtermBacktesterMultiThread(self, strategy: StrategyDataType, start_date: datetime, end_date: datetime, MAX_ACTIVE_PROCESS: int) -> TradeReportDataType:
        tradesData = []
        tradeReceivers = []
        active_process: list[multiprocessing.Process] = []
        currentDate = start_date
        while currentDate <= end_date:
            if len(active_process) < MAX_ACTIVE_PROCESS:
                rec, trans = multiprocessing.Pipe()
                # data = multiprocessing.Value(Optional[TradeDataType], None)
                process = multiprocessing.Process(target=self.testStrategyMultiThread,
                                                  args=(currentDate, strategy, trans,))
                active_process.append(process)
                tradeReceivers.append(rec)
                currentDate = currentDate + timedelta(days=1)
            else:
                while len(active_process) != 0:
                    process = active_process.pop()
                    process.start()

                while len(tradeReceivers) != 0:
                    rec = tradeReceivers.pop()
                    trade = rec.recv()
                    if trade != None:
                        tradesData.append(trade)

        while len(active_process) != 0:
            process = active_process.pop()
            process.start()

        while len(tradeReceivers) != 0:
            rec = tradeReceivers.pop()
            trade = rec.recv()
            if trade != None:
                tradesData.append(trade)

        tradeReport = self.generateTradeReport(tradesData)
        return tradeReport

    def testStrategyMultiThread(self, date: datetime, strategy: StrategyDataType, connection: multiprocessing.Pipe):
        tradeData = self.testStrategy(date, strategy)
        connection.send(tradeData)
        return

    def testStrategy(self, date: datetime, strategy: StrategyDataType) -> Optional[TradeDataType]:
        if date.strftime("%A").lower() not in strategy.entry.included_days and len(strategy.entry.included_days) != 0:
            return None
        dailyData = self.optionsDataService.getDailyData(date)
        filteredData = self.optionsDataService.filterDailyData(
            dailyData, [strategy.ticker])
        output: TradeDataType = None

        if len(filteredData) == 0:
            return None

        candleTimestamp = [key for key in filteredData[strategy.ticker].keys()]
        candleTimestamp.sort(reverse=False)
        for timestamp in candleTimestamp:
            candleData = filteredData[strategy.ticker][timestamp]
            if output == None:
                output = self.enterTrade(
                    date, strategy, candleData, dailyData)
            else:
                output = self.exitTrade(
                    output, date, strategy, candleData, dailyData)

        return output

    def enterTrade(self, date: datetime, strategy: StrategyDataType, candleData: CandleStickDataType, dailyData: dict[str, dict[int, CandleStickDataType]]) -> Optional[TradeDataType]:
        # filter data before entry time
        entryDatetime = date + timedelta(
            hours=int(strategy.entry.time.strip().split(":")[0]),
            minutes=int(strategy.entry.time.strip().split(":")[1]),
            seconds=int(strategy.entry.time.strip().split(":")[2]) if len(
                strategy.entry.time.strip().split(":")) == 3 else 0
        )
        exitDatetime = date + timedelta(
            hours=int(strategy.exit.time.strip().split(":")[0]),
            minutes=int(strategy.exit.time.strip().split(":")[1]),
            seconds=int(strategy.exit.time.strip().split(":")[2]) if len(
                strategy.entry.time.strip().split(":")) == 3 else 0
        )

        candleDatetime = datetime.fromtimestamp(candleData.timestamp)
        if entryDatetime > candleDatetime or candleDatetime > exitDatetime:
            return None

        atm_strike = getAtmStrike(candleData.open, candleData.ticker)

        optionTickers = []
        hedgeTickers = []
        for spreadOrder in strategy.spread.order:
            ticker = getTickerName(
                strategy.ticker, atm_strike, spreadOrder.strike, spreadOrder.contract_type)
            optionTickers.append(ticker)

            if spreadOrder.hedge_strike != "":
                hedge_ticker = getTickerName(
                    strategy.ticker, atm_strike, spreadOrder.hedge_strike, spreadOrder.contract_type)
                hedgeTickers.append(hedge_ticker)

        optionsCandleData = self.optionsDataService.filterOneCandleData(
            dailyData, optionTickers, candleData.timestamp)

        hedgesCandleData = self.optionsDataService.filterOneCandleData(
            dailyData, hedgeTickers, candleData.timestamp)

        if len(optionTickers) != len(optionsCandleData.keys()):
            return None

        if len(hedgeTickers) != len(hedgesCandleData.keys()):
            return None

        orders = []
        for spreadOrder in strategy.spread.order:
            ticker = getTickerName(
                strategy.ticker, atm_strike, spreadOrder.strike, spreadOrder.contract_type)
            order = placeOrder(ticker, optionsCandleData,
                               spreadOrder.order_side, spreadOrder.stoploss_percent)
            orders.append(order)
            # place hedge order also
            if spreadOrder.hedge_strike != "":
                hedge_ticker = getTickerName(
                    strategy.ticker, atm_strike, spreadOrder.hedge_strike, spreadOrder.contract_type)
                order = placeOrder(hedge_ticker, hedgesCandleData,
                                   spreadOrder.order_side.getOppositeSide(), spreadOrder.stoploss_percent)
                orders.append(order)

        output = TradeDataType(
            leverage=1,
            spread=[],
            quantity=1,
            atm_strike=atm_strike,
            entry_time=candleData.timestamp,
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
            underlying_data=[candleData.open]
        )

        return output

    def exitTrade(self, tradeData: TradeDataType, date: datetime, strategy: StrategyDataType, candleData: CandleStickDataType, dailyData: dict[str, dict[int, CandleStickDataType]]) -> Optional[TradeDataType]:
        tradeData.underlying_data.append(candleData.open)
        allTickers = getAllTickers(tradeData)
        activeTickers = getActiveTickers(tradeData)

        if len(activeTickers) == 0:
            return tradeData

        optionsCandleData = self.optionsDataService.filterOneCandleData(
            dailyData, allTickers, candleData.timestamp)

        if len(allTickers) != len(optionsCandleData.keys()) and tradeData.status == TradeStatusEnum.ENTERED:
            return None

        exitDatetime = date + timedelta(
            hours=int(strategy.exit.time.strip().split(":")[0]),
            minutes=int(strategy.exit.time.strip().split(":")[1]),
            seconds=int(strategy.exit.time.strip().split(":")[2]) if len(
                strategy.entry.time.strip().split(":")) == 3 else 0
        )

        # exit condition if current time exceeds max time
        candleDatetime = datetime.fromtimestamp(candleData.timestamp)
        if candleDatetime >= exitDatetime:
            tradeData = self.processRemainingExitLegs(
                tradeData, optionsCandleData)

        # exit condition when stoploss hits
        for spreadOrder in strategy.spread.order:
            tempTicker = getTickerName(
                strategy.ticker, tradeData.atm_strike, spreadOrder.strike, spreadOrder.contract_type)
            if tempTicker not in activeTickers:
                continue
            activeCandleData = optionsCandleData[tempTicker]
            oppositeOrder = getOrderData(tradeData.entry_orders, tempTicker)
            if checkIfLegStopLossHit(oppositeOrder, activeCandleData):
                if strategy.spread.stoploss_condition == SpreadStoplossConditionTypeEnum.EXIT_ONE_LEG:
                    tradeData = self.processExitLeg(
                        tempTicker, tradeData, optionsCandleData, strategy)
                else:
                    tradeData = self.processRemainingExitLegs(
                        tradeData, optionsCandleData)
                tradeData.stoploss_hit_strikes[tempTicker] = activeCandleData.open

        tradeData = updateProfitAndLoss(tradeData, optionsCandleData)

        # exit condition when take profit hits
        if checkIfTakeProfitHit(tradeData, strategy, candleData):
            tradeData = self.processRemainingExitLegs(
                tradeData, optionsCandleData)

        # exit condition when MTM stoploss hits
        if checkIfMTMStopLossHit(tradeData, strategy, candleData):
            tradeData = self.processRemainingExitLegs(
                tradeData, optionsCandleData)

        # exit condition when trailing stoploss hits
        if checkIfTrailingStopLossHit(tradeData, strategy):
            tradeData = self.processRemainingExitLegs(
                tradeData, optionsCandleData)

        tradeData = updateProfitAndLoss(tradeData, optionsCandleData)

        return tradeData

    def processExitLeg(self, ticker: str, tradeData: TradeDataType, optionsCandleData: dict[str, CandleStickDataType], strategy: StrategyDataType) -> TradeDataType:
        activeTickers = getActiveTickers(tradeData)
        legTickers = []
        for tempSpreadOrder in strategy.spread.order:
            tempTicker = getTickerName(
                strategy.ticker, tradeData.atm_strike, tempSpreadOrder.strike, tempSpreadOrder.contract_type)
            if ticker != tempTicker:
                continue
            # condition in case leg is already exited
            if tempTicker not in activeTickers:
                return tradeData

            legTickers.append(tempTicker)
            if tempSpreadOrder.hedge_strike != "":
                hedge_ticker = getTickerName(
                    strategy.ticker, tradeData.atm_strike, tempSpreadOrder.hedge_strike, tempSpreadOrder.contract_type)
                legTickers.append(hedge_ticker)

        for tempTicker in legTickers:
            order = placeOrder(tempTicker, optionsCandleData, getOppositeOrderSide(
                tradeData.entry_orders, tempTicker), -1)
            tradeData.exit_orders.append(order)

        return tradeData

    def processRemainingExitLegs(self, tradeData: TradeDataType, optionsCandleData: dict[str, CandleStickDataType]) -> TradeDataType:
        activeTickers = getActiveTickers(tradeData)
        for ticker in activeTickers:
            order = placeOrder(ticker, optionsCandleData, getOppositeOrderSide(
                tradeData.entry_orders, ticker), -1)
            tradeData.exit_orders.append(order)

        return tradeData

    def generateTradeReport(self, tradesData: list[TradeDataType]) -> TradeReportDataType:
        totalROI = 0
        totalWinners = 0
        totalLosers = 0
        maxWinner = 0
        maxLoser = 0
        totalWinPoints = 0
        totalLostPoints = 0
        for tradeData in tradesData:

            totalROI = totalROI + tradeData.pnl[len(tradeData.pnl) - 1].points

            if tradeData.trade_output == TradeOutputEnum.WINNER:
                totalWinPoints = totalWinPoints + \
                    tradeData.pnl[len(tradeData.pnl) - 1].points
                totalWinners = totalWinners + 1
                if tradeData.pnl[len(tradeData.pnl) - 1].points > maxWinner:
                    maxWinner = tradeData.pnl[len(tradeData.pnl) - 1].points
            else:
                totalLostPoints = totalLostPoints + \
                    tradeData.pnl[len(tradeData.pnl) - 1].points
                totalLosers = totalLosers + 1
                if tradeData.pnl[len(tradeData.pnl) - 1].points < maxLoser:
                    maxLoser = tradeData.pnl[len(tradeData.pnl) - 1].points

        return TradeReportDataType(
            total_points_captured=totalROI,
            total_trades=len(tradesData),
            total_won_points=totalWinPoints,
            total_won_trades=totalWinners,
            max_won_point=maxWinner,
            total_lost_points=totalLostPoints,
            total_lost_trades=totalLosers,
            max_lost_point=maxLoser

        )
