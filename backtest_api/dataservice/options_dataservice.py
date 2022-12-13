from multiprocessing.managers import BaseManager
import csv
from datetime import datetime
import os
from time import time
from backtest_api.models.candleStick import CandleStickDataType


DATA_PATH = "./data/weekly_data/"


class OptionsDataService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OptionsDataService, cls).__new__(cls)
        return cls._instance

    def __init__(self, MAX_CACHE_LENGTH: int = 4) -> None:
        self.dataCache = {}
        self.cachedFiles = []
        self.MAX_CACHE_LENGTH = MAX_CACHE_LENGTH
        return

    def __getDataFilename(self, date: datetime) -> str:
        dir_list = os.listdir(DATA_PATH)
        for file in dir_list:
            if not file.endswith(".csv"):
                continue

            startDateStr = file.split("_")[0]
            endDateStr = file.split("_")[1]

            startDate = datetime(int(startDateStr.split("-")[0]), int(
                startDateStr.split("-")[1]), int(startDateStr.split("-")[2].replace(".csv", "")))

            endDate = datetime(int(endDateStr.split("-")[0]), int(
                endDateStr.split("-")[1]), int(endDateStr.split("-")[2].replace(".csv", "")))

            if date >= startDate and date <= endDate:
                return file

        return None

    def __readOptionsCsvFile(self, filename: str) -> dict:
        output = []

        with open(DATA_PATH + filename, mode='r')as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                if lines[0].strip().lower() == '':
                    continue
                if lines[0].strip().lower() == 'ticker':
                    continue

                date = lines[1].strip().split(" ")[0]
                time = lines[1].strip().split(" ")[1]

                dateEntries = date.split("-")
                timeEntries = time.split(":")

                timestamp = datetime(
                    int(dateEntries[2]),
                    int(dateEntries[1]),
                    int(dateEntries[0]),
                    int(timeEntries[0]),
                    int(timeEntries[1]),
                    int(timeEntries[2]) if len(timeEntries) == 3 else 0
                )

                output.append(
                    {
                        "ticker": lines[0].lower().strip(),
                        "timestamp": int(timestamp.timestamp()),
                        "open": float(lines[2].lower().strip()),
                        "high": float(lines[3].lower().strip()),
                        "low": float(lines[4].lower().strip()),
                        "close": float(lines[5].lower().strip()),
                        "volume": int(lines[6].lower().strip()),
                        "open_interest": int(lines[7].lower().strip())
                    }
                )

        return output

    def getDailyData(self, date: datetime) -> dict[str, dict[int, CandleStickDataType]]:
        outputData: dict[str, dict[int, CandleStickDataType]] = {}

        filename = self.__getDataFilename(date)
        if filename == None:
            return {}

        if filename not in self.cachedFiles:
            fileData = self.__readOptionsCsvFile(filename)
            self.dataCache[filename] = fileData
            self.cachedFiles.append(filename)
            if len(self.cachedFiles) > self.MAX_CACHE_LENGTH:
                self.cachedFiles.pop()
        else:
            fileData = self.dataCache[filename]

        for candleStickRaw in fileData:
            dataDate = datetime.fromtimestamp(candleStickRaw["timestamp"])
            if date.day != dataDate.day or date.month != dataDate.month or date.year != dataDate.year:
                continue

            candleStick = CandleStickDataType(**candleStickRaw)
            if candleStick.ticker in outputData.keys():
                outputData[candleStick.ticker][candleStick.timestamp] = candleStick
            else:
                outputData[candleStick.ticker] = {
                    candleStick.timestamp: candleStick}

        return outputData

    def filterDailyData(self, data: dict[str, dict[int, CandleStickDataType]], tickers: list[str]) -> dict[str, dict[int, CandleStickDataType]]:
        outputData: dict[str, dict[int, CandleStickDataType]] = {}

        for ticker in tickers:
            if ticker.lower() in data.keys():
                outputData[ticker] = data[ticker]

        return outputData

    def filterOneCandleData(self, data: dict[str, dict[int, CandleStickDataType]], tickers: list[str], timestamp: int) -> dict[str, CandleStickDataType]:
        outputData: dict[str, CandleStickDataType] = {}

        for ticker in tickers:
            if ticker in data.keys():
                if timestamp in data[ticker].keys():
                    outputData[ticker] = data[ticker][timestamp]

        return outputData
