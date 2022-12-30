from functools import lru_cache
from backend_process.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend_process.dataservice.historicalOhlcDataService import HistoricalOhlcDataService
from backend_process.dataservice.historical_dataservice import HistoricalDataService
from backend_process.usecase.strategy_tester import StrategyBackTester
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
