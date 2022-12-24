from functools import lru_cache
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.dataservice.historicalOhlcDataService import HistoricalOhlcDataService
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.usecase.strategy_tester import StrategyBackTester
from ..model import setting


def getIntradayBacktestCrud() -> IntradayBackTesterCrud:
    settings = get_settings()
    historicalDataService = HistoricalDataService(settings.DATA_URL)
    cashDataService = HistoricalOhlcDataService("./data/")
    strategyTester = StrategyBackTester(cashDataService)
    crud = IntradayBackTesterCrud(strategyTester)
    return crud


@lru_cache()
def get_settings():
    return setting.Settings()
