from datetime import datetime, timedelta
from typing import Optional, Any, Union
from model.setting import Settings
from model.baseModel import CustomBaseModel
from model.strategy import StrategyDataType
from model.trade import TradeDataType, TradeDetailedDataType, TradeOutputEnum, TradeReportDataType
import requests
import threading
import time


class DistributedResponseType(CustomBaseModel):
    statusCode: int
    time: float
    tradeData: Optional[Union[TradeReportDataType, TradeDetailedDataType]]
    error: Optional[str]


class OptionsBacktestOrchestratorCrud:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        return

    def __processRequest(self, strategy: StrategyDataType, start_date: datetime, end_date: datetime, output: list[DistributedResponseType], detailed: bool = False):
        params = {
            "start_date_day": start_date.day,
            "start_date_month": start_date.month,
            "start_date_year": start_date.year,

            "end_date_day": end_date.day,
            "end_date_month": end_date.month,
            "end_date_year": end_date.year
        }
        start_time = datetime.now()
        url = self.settings.PROCESS_URL if not detailed else self.settings.PROCESS_URL + 'detailed'
        response = requests.post(
            url=url, json=strategy.dict(), params=params)

        end_time = datetime.now()
        try:
            formattedResponse = DistributedResponseType(
                statusCode=response.status_code,
                time=float((end_time - start_time).microseconds/1000),
                tradeData=TradeReportDataType(
                    **response.json()) if not detailed else TradeDetailedDataType(**response.json())
            )
        except Exception as e:
            formattedResponse = DistributedResponseType(
                statusCode=response.status_code,
                time=float((end_time - start_time).microseconds/1000),
                error=str(e)
            )
        output.append(formattedResponse)

    def __getMaxThreads(self, start_date: datetime, end_date: datetime):
        total_days = (end_date - start_date).days + 1
        if total_days < self.settings.MAX_THREADS:
            return total_days

        return self.settings.MAX_THREADS

    def testStrategy(self, start_date: datetime, end_date: datetime, strategy: StrategyDataType, detailed: bool = False) -> Optional[TradeReportDataType]:

        start = time.time()
        output: list[DistributedResponseType] = []

        self.__processRequest(strategy, start_date, end_date, output, detailed)

        end = time.time()

        return self.clubTradeReport(output, end-start, detailed=detailed)

    def testStrategyDistributed(self, start_date: datetime, end_date: datetime, strategy: StrategyDataType, detailed: bool = False) -> Optional[TradeReportDataType]:
        max_threads = self.__getMaxThreads(start_date, end_date)

        start = time.time()
        output: list[DistributedResponseType] = []
        index = 0
        threadPool: list[threading.Thread] = []
        currentDate = start_date
        while index < max_threads:
            total_days_left = (end_date - currentDate).days + 1
            days_per_thread = int(total_days_left/(max_threads - index))
            temp_end_date = currentDate + \
                timedelta(days=days_per_thread - 1)
            if temp_end_date > end_date:
                temp_end_date = end_date
            process = threading.Thread(
                target=self.__processRequest, args=(strategy, currentDate, temp_end_date, output, detailed,))
            threadPool.append(process)
            process.start()
            index = index + 1
            currentDate = temp_end_date + timedelta(days=1)

        while len(threadPool) != 0:
            thread = threadPool.pop()
            thread.join()
        end = time.time()

        return self.clubTradeReport(output, end-start, max_threads, detailed)

    def clubTradeReport(self, tradeReports: list[DistributedResponseType], totalTime: float, max_threads: int = 1, detailed: bool = False) -> Union[TradeReportDataType, TradeDetailedDataType]:
        if detailed:
            output = TradeDetailedDataType(
                tradeData=[]
            )
            for entry in tradeReports:
                output.tradeData = output.tradeData + entry.tradeData.tradeData
            
            return output
            
        
        total_failed = 0
        average_time = 0.0
        max_time = 0
        tradeOutput = {}
        for entry in tradeReports:
            if entry.statusCode != 200:
                total_failed = total_failed + 1
                continue

            tradeReportDict = entry.tradeData.dict()
            for key in tradeReportDict.keys():
                if key in tradeOutput.keys():
                    tradeOutput[key] = tradeOutput[key] + tradeReportDict[key]
                else:
                    tradeOutput[key] = tradeReportDict[key]

            average_time = average_time + entry.time/max_threads

            if max_time < entry.time:
                max_time = entry.time

        tradeOutput = TradeReportDataType(**tradeOutput)
        tradeOutput.average_request_time = average_time
        tradeOutput.max_request_time = max_time
        tradeOutput.total_time = totalTime
        tradeOutput.total_failed_percent = total_failed*100/max_threads

        return tradeOutput
