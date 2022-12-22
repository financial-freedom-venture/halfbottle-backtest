from __future__ import annotations
from datetime import datetime
from enum import Enum
from math import isnan
from typing import Optional
from backend.models.baseModel import CustomBaseModel
import pandas as pd


class InstrumentTypeEnum(str, Enum):
    FUTURES = "futures"
    CASH = "cash"
    OPTIONS = "options"


class ContractTypeEnum(str, Enum):
    CALL = "call"
    PUT = "put"


class ExpiryTypeEnum(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TimeFrameTypeEnum(str, Enum):
    SECOND_1 = "1second"
    MINUTE_1 = "1minute"
    MINUTE_3 = "3minute"
    MINUTE_5 = "5minute"
    MINUTE_15 = "15minute"
    MINUTE_30 = "30minute"
    HOUR_1 = "1hour"
    HOUR_2 = "2hour"
    HOUR_4 = "4hour"
    DAY_1 = "1day"
    WEEK_1 = "1week"
    MONTH_1 = "1month"
    YEAR_1 = "1year"


class CandleStickDataType(CustomBaseModel):
    ticker: str
    open: float
    high: float
    low: float
    close: float
    timestamp: int
    iso_string: str
    volume: int
    open_interest: Optional[int]
    strike: Optional[int]
    expiry_type: Optional[str]
    expiry: Optional[str]
    instrument: Optional[InstrumentTypeEnum]
    contract_type: Optional[ContractTypeEnum]
    timeframe: TimeFrameTypeEnum


class CandleStickListDataType(CustomBaseModel):
    data: list[CandleStickDataType]

    def generatePandasDf(self) -> pd.DataFrame:

        dfData = [
            [
                entry.timestamp,
                entry.open,
                entry.high,
                entry.low,
                entry.close,
                entry.volume,
                entry.open_interest,
                entry.strike,
                entry.expiry_type,
                entry.expiry,
                entry.instrument,
                entry.contract_type
            ]
            for entry in self.data
        ]

        df = pd.DataFrame(
            dfData,
            columns=[
                'timestamp',
                'open',
                'high',
                'low',
                'close',
                'volume',
                'open_interest',
                'strike',
                'expiry_type',
                'expiry',
                'instrument',
                'contract_type'
            ]
        )

        return df

    @staticmethod
    def generateFromPandasDf(ticker: str, df: pd.DataFrame, timeframe: TimeFrameTypeEnum) -> CandleStickListDataType:
        output = CandleStickListDataType(data=[])
        for index, row in df.iterrows():
            output.data.append(CandleStickDataType(
                ticker=ticker,
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                timestamp=row["timestamp"],
                iso_string=datetime.fromtimestamp(
                    row["timestamp"]/1000).isoformat(),
                volume=row["volume"],

                open_interest=row["open_interest"] if not isnan(
                    row["open_interest"]) else None,
                strike=row["strike"] if not isnan(
                    row["strike"]) else None,
                expiry_type=row["expiry_type"] if not isnan(
                    row["strike"]) else None,
                expiry=row["expiry"] if not isnan(
                    row["strike"]) else None,
                instrument=row["instrument"],
                contract_type=row["contract_type"] if not isnan(
                    row["strike"]) else None,
                timeframe=timeframe
            ))

        return output


class CandleStickDictDataType(CustomBaseModel):
    data: dict[int, CandleStickDataType]


class SortType(CustomBaseModel):
    INCREASING = "increasing"
    DECREASING = "decreasing"


class CandleDataList(CustomBaseModel):
    time_frame: str
    data: list[CandleStickDataType]
