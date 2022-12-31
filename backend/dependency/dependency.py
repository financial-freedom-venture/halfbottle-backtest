from functools import lru_cache
from backend.crud.optionsBacktestOrchestratorCrud import OptionsBacktestOrchestratorCrud
from model import setting


def getOptionsBacktestOrchestratorCrud() -> OptionsBacktestOrchestratorCrud:
    settings = get_settings()
    crud = OptionsBacktestOrchestratorCrud(settings)
    return crud


@lru_cache()
def get_settings():
    return setting.Settings()
