from datetime import datetime
from typing import Optional
from backend.models.strategy import StrategyDataType
from backend.models.trade import TradeDataType
from backend.usecases.strategy_tester import StrategyBackTester


class IntradayBackTesterCrud:

    def __init__(self, strategyTesterService: StrategyBackTester) -> None:
        self.strategyTesterService = strategyTesterService
        return

    def testStrategy(self, date: datetime, strategy: StrategyDataType) -> Optional[TradeDataType]:
        tradeData = self.strategyTesterService.testStrategy(date, strategy)
        return tradeData
