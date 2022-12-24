from datetime import datetime
import json
from typing import Optional, Union
from backend.dataservice.historicalOhlcDataService import HistoricalOhlcDataService
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.dto.entryDto import TradeEntryConditionResponseDTO, TradeEntryTypeEnum
from backend.dto.exitDto import TradeExitConditionResponseDTO, TradeExitTypeEnum
from backend.model.candleStick import CandleStickDataType, CandleStickDictDataType
from backend.model.strategy import StrategyDataType
from backend.usecase.entry_condition import checkEntryCondition
from backend.usecase.exit_condition import checkExitCondition
from backend.model.trade import TradeDataType, TradeOutputEnum, TradeStatusEnum
from backend.usecase.order_helper import placeEntryOrders, processExitLeg, processRemainingExitLegs
from backend.usecase.strategy_helper import updateProfitAndLoss
from backend.utils.candleUtils import convertFastAccessData, getMostRecentCandle
from backend.utils.strategyUtil import getSpreadOrderStrike


DATA_PATH = "./strategy/"


class StrategyBackTester:

    def __init__(self, historicalDataService: Union[HistoricalDataService, HistoricalOhlcDataService]) -> None:
        self.historicalDataService = historicalDataService
        return

    def loadStrategy(self, filename) -> Optional[StrategyDataType]:
        jsonData = json.load(open(DATA_PATH + filename))

        try:
            strategyData = StrategyDataType(**jsonData)
            return strategyData
        except Exception as e:
            return None

    def loadTickerData(self, date: datetime, strategy: StrategyDataType) -> Optional[dict[str, CandleStickDictDataType]]:
        output = {}

        # get ticker data
        data = self.historicalDataService.getCashData(strategy.ticker, date)
        if data == None:
            return None
        output[strategy.ticker.upper()] = data

        # format output
        return convertFastAccessData(output)

    def loadOptionsData(self,  strategy: StrategyDataType, underlyingCandle: CandleStickDataType) -> Optional[dict[str, CandleStickDictDataType]]:
        candleDatetime = datetime.fromtimestamp(underlyingCandle.timestamp)
        date = datetime(candleDatetime.year,
                        candleDatetime.month, candleDatetime.day)
        output = {}
        for order in strategy.spread.order:
            strike = getSpreadOrderStrike(
                underlyingCandle.ticker, underlyingCandle.open, order.strike)
            data = self.historicalDataService.getOptionsData(
                underlyingCandle.ticker, strike, strategy.expiry, order.contract_type, date)
            if data == None:
                return None
            output[str(strike)+order.contract_type] = data
            if order.hedge_strike != None:
                hedge_strike = getSpreadOrderStrike(
                    strategy.ticker, underlyingCandle.open, order.hedge_strike)
                data = self.historicalDataService.getOptionsData(
                    underlyingCandle.ticker, hedge_strike, strategy.expiry, order.contract_type, date)
                if data == None:
                    return None
                output[str(hedge_strike)+order.contract_type] = data

        # format output
        return convertFastAccessData(output)

    def testStrategy(self, date: datetime, strategy: StrategyDataType) -> Optional[TradeDataType]:
        if date.strftime("%A").lower() not in strategy.entry.included_days and len(strategy.entry.included_days) != 0:
            return None

        data = self.loadTickerData(date, strategy)
        if data == None:
            return None

        return self.executeStrategy(strategy, data)

    def executeStrategy(self, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDictDataType]) -> Optional[TradeDataType]:
        output: TradeDataType = None

        candleTimestamp = [
            key for key in candleStickData[strategy.ticker.upper()].data.keys()]
        candleTimestamp.sort(reverse=False)
        for timestamp in candleTimestamp:
            currentCandleData = getMostRecentCandle(timestamp, candleStickData)

            # check entry
            entryDto = checkEntryCondition(
                output, timestamp, strategy, currentCandleData)
            if entryDto.entry_type == TradeEntryTypeEnum.COMPLETE_ENTRY:
                optionsCandleData = self.loadOptionsData(
                    strategy, currentCandleData[strategy.ticker])
                if optionsCandleData == None:
                    return None
                candleStickData = candleStickData | optionsCandleData
                currentCandleData = getMostRecentCandle(
                    timestamp, candleStickData)
                output = self.__enterTradeCompleteTrade(
                    timestamp, strategy, entryDto, currentCandleData)

            exitDto = checkExitCondition(
                output, timestamp, strategy, currentCandleData)
            if exitDto.exit_type == TradeExitTypeEnum.COMPLETE_EXIT:
                output = self.__exitCompleteTrade(
                    timestamp, output, strategy, exitDto, currentCandleData)
                return updateProfitAndLoss(output, currentCandleData)
            elif exitDto.exit_type == TradeExitTypeEnum.PARTIAL_EXIT:
                output = self.__exitPartialTrade(
                    timestamp, output, strategy, exitDto, currentCandleData)

            if output != None:
                output = updateProfitAndLoss(output, currentCandleData)

        return output

    def __enterTradeCompleteTrade(self, timestamp: int, strategy: StrategyDataType, entryData: TradeEntryConditionResponseDTO, candleStickData: dict[str, CandleStickDataType]) -> Optional[TradeDataType]:
        if entryData.entry_type != TradeEntryTypeEnum.COMPLETE_ENTRY:
            return None

        atm_strike, orders = placeEntryOrders(
            timestamp, strategy, candleStickData)

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
                candleStickData[strategy.ticker].open]
        )
        return output

    def __exitCompleteTrade(self, timestamp: int, tradeData: TradeDataType, strategy: StrategyDataType, exitData: TradeExitConditionResponseDTO, candleStickData: dict[str, CandleStickDataType]) -> TradeDataType:
        return processRemainingExitLegs(
            tradeData, candleStickData)

        return tradeData

    def __exitPartialTrade(self, timestamp: int, tradeData: TradeDataType, strategy: StrategyDataType, exitData: TradeExitConditionResponseDTO, candleStickData: dict[str, CandleStickDataType]) -> TradeDataType:
        for order in exitData.data.orders:
            tradeData = processExitLeg(
                order, tradeData, strategy, candleStickData)
        return tradeData
