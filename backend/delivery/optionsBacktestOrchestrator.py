from datetime import datetime
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from backend.crud.optionsBacktestOrchestratorCrud import OptionsBacktestOrchestratorCrud
from backend.dependency.dependency import getOptionsBacktestOrchestratorCrud
from model.strategy import StrategyDataType


router = APIRouter()


########################################################
#                      Endpoints                       #
########################################################
@router.post("/distributed", status_code=200)
def getDistributedTest(
    request: Request,
    start_date_day: int,
    start_date_month: int,
    start_date_year: int,
    end_date_day: int,
    end_date_month: int,
    end_date_year: int,
    requestData: StrategyDataType,
    crud: OptionsBacktestOrchestratorCrud = Depends(
        getOptionsBacktestOrchestratorCrud)
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

    data = crud.testStrategyDistributed(start_date, end_date, requestData)

    if data == None:
        raise HTTPException(
            status_code=403, detail="Data not available on this date or No Entry Available"
        )

    return data.dict()


########################################################
#                      Endpoints                       #
########################################################
@router.post("/distributed/detailed", status_code=200)
def getDistributedTest(
    request: Request,
    start_date_day: int,
    start_date_month: int,
    start_date_year: int,
    end_date_day: int,
    end_date_month: int,
    end_date_year: int,
    requestData: StrategyDataType,
    crud: OptionsBacktestOrchestratorCrud = Depends(
        getOptionsBacktestOrchestratorCrud)
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
