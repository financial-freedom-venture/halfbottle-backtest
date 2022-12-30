from datetime import datetime
from typing import Optional
from fastapi import Request
import requests

from backend_process.model.candleStick import CandleStickListDataType, ContractTypeEnum, ExpiryTypeEnum


DATA_PATH = "./data/weekly_data/"


class HistoricalDataService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        return

    def getCashData(self, ticker: str, datetime: datetime) -> Optional[CandleStickListDataType]:
        url = self.base_url + "historical/ohlc/cash/"
        params = {"ticker": ticker.upper(), "date_day": datetime.day,
                  "date_month": datetime.month, "date_year": datetime.year}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return None

        return CandleStickListDataType(**response.json()["data"])

    def getOptionsData(self, ticker: str, strike: int, expiry_type: ExpiryTypeEnum, contract_type: ContractTypeEnum, datetime: datetime) -> Optional[CandleStickListDataType]:
        url = self.base_url + "historical/ohlc/options/strike"
        params = {"ticker": ticker.upper(), "strike": strike, "expiry_type": expiry_type, "contract_type": contract_type, "date_day": datetime.day,
                  "date_month": datetime.month, "date_year": datetime.year}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return None

        return CandleStickListDataType(**response.json()["data"])
