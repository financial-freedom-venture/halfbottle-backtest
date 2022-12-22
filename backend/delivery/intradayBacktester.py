from datetime import datetime
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.dependency.dependency import getIntradayBacktestCrud
from backend.models.strategy import StrategyDataType
from backend.usecases.strategy_tester import StrategyBackTester


router = APIRouter()


########################################################
#                      Endpoints                       #
########################################################
@router.post("/", status_code=200)
def getIntradayTest(
    request: Request,
    date_day: int,
    date_month: int,
    date_year: int,
    requestData: StrategyDataType,
    crud: IntradayBackTesterCrud = Depends(getIntradayBacktestCrud)
):
    try:
        date = datetime(date_year, date_month, date_day)
    except Exception as e:
        logging.warning(
            f'intradayBacktest -- getIntradayTest Daily --> Validation error in date')
        logging.warning(e)
        raise HTTPException(
            status_code=400, detail="invalid dates provided"
        )

    data = crud.testStrategy(date, requestData)

    if data == None:
        raise HTTPException(
            status_code=403, detail="Data not available on this date"
        )

    return data.dict()
