from functools import lru_cache
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.usecases.strategy_tester import StrategyBackTester
from ..models import setting


def getIntradayBacktestCrud() -> IntradayBackTesterCrud:
    settings = get_settings()
    historicalDataService = HistoricalDataService(settings.DATA_URL)
    strategyTester = StrategyBackTester(historicalDataService)
    crud = IntradayBackTesterCrud(strategyTester)
    return crud


@lru_cache()
def get_settings():
    return setting.Settings()
