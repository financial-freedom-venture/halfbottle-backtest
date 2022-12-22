from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.models.strategy import StrategyDataType
from backend.usecases.strategy_tester import StrategyBackTester


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
    optionsDatastore = HistoricalDataService()
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
