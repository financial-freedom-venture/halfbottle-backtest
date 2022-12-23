from datetime import datetime
from backend.datastore.csvDataStore import CsvDataStore
from backend.model.candleStick import CandleStickListDataType, ContractTypeEnum, ExpiryTypeEnum, TimeFrameTypeEnum
from backend.model.error import ErrorResponse
from typing import Tuple, Optional


class HistoricalOhlcDataService:

    def __init__(self, data_path: str) -> None:
        self.store = CsvDataStore(data_path)
        return

    def getCashData(self, ticker: str, date: datetime) -> Optional[CandleStickListDataType]:

        output, err = self.store.getCashData(ticker, date)

        if err != None:
            # return None, err
            return None

        candleData = CandleStickListDataType.generateFromPandasDf(
            ticker, output, TimeFrameTypeEnum.MINUTE_1)

        return candleData

    def getOptionsData(
        self,
        ticker: str,
        strike: int,
        expiry_type: ExpiryTypeEnum,
        contract_type: ContractTypeEnum,
        date: datetime
    ) -> Optional[CandleStickListDataType]:

        output, err = self.store.getOptionsData(
            ticker, expiry_type, strike, contract_type, date)

        if err != None:
            return None

        candleData = CandleStickListDataType.generateFromPandasDf(
            ticker, output, TimeFrameTypeEnum.MINUTE_1)

        return candleData
