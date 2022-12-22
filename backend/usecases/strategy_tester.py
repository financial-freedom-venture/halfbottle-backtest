from datetime import datetime
import json
from typing import Optional
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.models.candleStick import CandleStickDictDataType
from backend.models.strategy import StrategyDataType
from backend.usecases.strategy_executer import enterTrade, exitTrade
from backend.models.trade import TradeDataType, TradeStatusEnum
from backend.utils.candleUtils import convertFastAccessData
from backend.utils.strategyUtil import getSpreadOrderStrike


DATA_PATH = "./strategy/"


class StrategyBackTester:

    def __init__(self, historicalDataService: HistoricalDataService) -> None:
        self.historicalDataService = historicalDataService
        return

    def loadStrategy(self, filename) -> Optional[StrategyDataType]:
        jsonData = json.load(open(DATA_PATH + filename))

        try:
            strategyData = StrategyDataType(**jsonData)
            return strategyData
        except Exception as e:
            return None

    def loadData(self, date: datetime, strategy: StrategyDataType) -> Optional[dict[str, CandleStickDictDataType]]:
        output = {}

        # get ticker data
        data = self.historicalDataService.getCashData(strategy.ticker, date)
        if data == None:
            return None
        output[strategy.ticker.upper()] = data

        # format output
        return convertFastAccessData(output)

    def testStrategy(self, date: datetime, strategy: StrategyDataType) -> Optional[TradeDataType]:
        if date.strftime("%A").lower() not in strategy.entry.included_days and len(strategy.entry.included_days) != 0:
            return None

        data = self.loadData(date, strategy)
        if data == None:
            return None

        return self.executeStrategy(strategy, data)

    def executeStrategy(self, strategy: StrategyDataType, candleStickData: dict[str, CandleStickDictDataType]) -> Optional[TradeDataType]:
        output: TradeDataType = None

        candleTimestamp = [
            key for key in candleStickData[strategy.ticker.upper()].data.keys()]
        candleTimestamp.sort(reverse=False)
        for timestamp in candleTimestamp:
            # check if market is open
            if output == None or output.status == TradeStatusEnum.SEARCHING:
                candleStickData, output = enterTrade(
                    self.historicalDataService, timestamp, strategy, candleStickData)
            elif output.status == TradeStatusEnum.PARTIAL_EXIT or output.status == TradeStatusEnum.ENTERED:
                output = exitTrade(
                    output, timestamp, strategy, candleStickData)
            else:
                break

        return output
