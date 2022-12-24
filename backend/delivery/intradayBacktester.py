from datetime import datetime
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.dependency.dependency import getIntradayBacktestCrud
from backend.model.strategy import StrategyDataType
from backend.usecase.strategy_tester import StrategyBackTester


router = APIRouter()


########################################################
#                      Endpoints                       #
########################################################
@router.post("/", status_code=200)
def getIntradayTest(
    request: Request,
    start_date_day: int,
    start_date_month: int,
    start_date_year: int,
    end_date_day: int,
    end_date_month: int,
    end_date_year: int,
    requestData: StrategyDataType,
    crud: IntradayBackTesterCrud = Depends(getIntradayBacktestCrud)
):
    try:
        start_date = datetime(
            start_date_year, start_date_month, start_date_day)
        end_date = datetime(end_date_year, end_date_month, end_date_day)
    except Exception as e:
        logging.warning(
            f'intradayBacktest -- getIntradayTest Daily --> Validation error in date')
        logging.warning(e)
        raise HTTPException(
            status_code=400, detail="invalid dates provided"
        )

    data = crud.testStrategy(start_date, end_date, requestData)

    if data == None:
        raise HTTPException(
            status_code=403, detail="Data not available on this date or No Entry Available"
        )

    return data.dict()
