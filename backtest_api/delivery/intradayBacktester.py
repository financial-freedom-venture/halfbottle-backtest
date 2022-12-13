from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, HTTPException

from backtest_api.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backtest_api.dataservice.options_dataservice import OptionsDataService
from backtest_api.models.strategy import StrategyDataType
from backtest_api.usecases.strategy_tester import StrategyBackTester


router = APIRouter()


########################################################
#                      Endpoints                       #
########################################################
@router.post("/", status_code=200)
def getSympaiMapping(
    request: Request,
    date: str,
    requestData: StrategyDataType,
):
    optionsDatastore = OptionsDataService()
    strategyBacktestingService = StrategyBackTester(optionsDatastore)
    crud = IntradayBackTesterCrud(strategyBacktestingService)

    data = crud.testStrategy(
        datetime(
            int(date.split("-")[0]),
            int(date.split("-")[1]),
            int(date.split("-")[2])
        ),
        requestData
    )

    if data == None:
        raise HTTPException(
            status_code=403, detail="Data not available on this date"
        )

    return data.dict()
