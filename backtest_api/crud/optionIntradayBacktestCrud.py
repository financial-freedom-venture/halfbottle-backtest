from datetime import datetime
from typing import Optional
from backtest_api.models.strategy import StrategyDataType
from backtest_api.models.trade import TradeDataType
from backtest_api.usecases.strategy_tester import StrategyBackTester


class IntradayBackTesterCrud:

    def __init__(self, strategyTesterService: StrategyBackTester) -> None:
        self.strategyTesterService = strategyTesterService
        return

    def testStrategy(self, date: datetime, strategy: StrategyDataType) -> Optional[TradeDataType]:
        tradeData = self.strategyTesterService.testStrategy(date, strategy)
        return tradeData
