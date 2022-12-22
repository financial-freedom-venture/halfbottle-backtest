from functools import lru_cache
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.usecases.strategy_tester import StrategyBackTester
from ..models import setting


def getPostMarketDataCrud():
    settings = get_settings()
    StrategyBackTester()
    crud = IntradayBackTesterCrud()
    return crud


def getCashDataCrud() -> HistoricalOhlcDataCrud:
    settings = get_settings()
    authService = AuthenticationService(settings)
    cashDataService = HistoricalOhlcDataService("./data/")
    crud = HistoricalOhlcDataCrud(settings, cashDataService, authService)
    return crud


@lru_cache()
def get_settings():
    return setting.Settings()
