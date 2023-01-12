
from datetime import date, datetime, timedelta
import json
import logging
import os
from model.candleStick import CandleStickDataType, TimeFrameTypeEnum, CandleStickListDataType, InstrumentTypeEnum
import pandas as pd


directoryPath = "/Users/harshitagrawal/Desktop/projects/halfbottle/halfbottle-backtest/data/"

# ---------------------------------- Transform Functions ----------------------------------------#


def generateFiles(data: CandleStickListDataType, instrument: InstrumentTypeEnum) -> dict[str, CandleStickListDataType]:
    if instrument == InstrumentTypeEnum.CASH:
        return __generateCashFiles(data)

    if instrument == InstrumentTypeEnum.OPTIONS:
        return __generateOptionsFiles(data)
    return {}


#   folder format CASH
# data -> CASH -> TICKER -> YEAR -> DATE.json
# key is 2 things
#  - Ticker->>Date
def __generateCashFiles(data: CandleStickListDataType) -> dict[str, CandleStickListDataType]:
    output: dict[str, CandleStickListDataType] = {}
    for entry in data.data:
        datetime_ist = datetime.fromisoformat(
            entry.iso_string) - timedelta(minutes=330)
        key = entry.ticker + "->>" + str(datetime_ist.year) + "-" \
            + str(datetime_ist.month) + "-" \
            + str(datetime_ist.day)
        if key in output.keys():
            output[key].data.append(entry)
        else:
            output[key] = CandleStickListDataType(data=[entry])

    for key in output.keys():
        output[key].data.sort(key=lambda x: x.timestamp, reverse=False)

    return output


#   folder format FUT
# data -> OPTION -> TICKER -> EXPIRY TYPE -> EXPIRY -> DATE -> STRIKE-CONTRACT_TYPE.json
def __generateOptionsFiles(data: CandleStickListDataType) -> dict[str, CandleStickListDataType]:
    output: dict[str, CandleStickListDataType] = {}
    for entry in data.data:
        datetime_ist = datetime.fromisoformat(
            entry.iso_string) - timedelta(minutes=330)
        date_str = str(datetime_ist.year) + "-" \
            + str(datetime_ist.month) + "-" \
            + str(datetime_ist.day)
        key = entry.ticker + "-++" + entry.expiry_type + "-++" + entry.expiry + "-++" + \
            date_str + "-++" + str(entry.strike) + "-" + entry.contract_type
        if key in output.keys():
            output[key].data.append(entry)
        else:
            output[key] = CandleStickListDataType(data=[entry])

    for key in output.keys():
        output[key].data.sort(key=lambda x: x.timestamp, reverse=False)

    return output

#   folder format FUT
# data -> FUTURE -> TICKER -> EXPIRY -> DATE.json


def __generateFuturesFiles(data: CandleStickListDataType, date: date) -> dict[str, CandleStickListDataType]:
    return


# ---------------------------------- Write Functions ----------------------------------------#
def writeFiles(data: dict[str, CandleStickListDataType], instrument: InstrumentTypeEnum) -> bool:
    if len(data) == 0:
        logging.warning('IciciDataService -++ writeFiles: Not data found')
        return False
    if instrument == InstrumentTypeEnum.CASH:
        return __writeCashFiles(data)

    if instrument == InstrumentTypeEnum.OPTIONS:
        return __writeOptionsFiles(data)
    return False


# key can be 2 things
# key is 2 things
#  - Ticker->>Date
def __writeCashFiles(data: dict[str, CandleStickListDataType]) -> bool:
    for key in data.keys():
        ticker = key.split("->>")[0]
        key = key.split("->>")[1]
        directory = directoryPath + "CASH/" + ticker + "/"

        try:
            os.makedirs(directory)
        except FileExistsError:
            count = 1

        if os.path.exists(directory + key + ".csv"):
            continue

        df = data[ticker + "->>" + key].generatePandasDf()
        df.to_csv(directory + key + '.csv', sep=',')
        # with open(directory + key + '.json', 'w', encoding='utf-8') as f:
        #     json.dump(data[key].dict(), f, ensure_ascii=False, indent=4)
    return True


#   folder format FUT
# data -> OPTION -> TICKER -> EXPIRY TYPE -> EXPIRY-++EXPIRY -> DATE -> STRIKE-CONTRACT_TYPE.json
def __writeOptionsFiles(data: dict[str, CandleStickListDataType]) -> bool:
    for key in data.keys():
        keyData = key.split("-++")
        ticker = keyData[0].upper()
        expiry_type = keyData[1].upper()
        expiry = keyData[2].upper()
        date = keyData[3].upper()
        filename = keyData[4].upper()

        directory = directoryPath + "OPTIONS/" + \
            ticker + "/" + expiry_type + "/" + "EXPIRY-++" + expiry.split("T")[0] + \
            "/" + date + "/"
        try:
            os.makedirs(directory)
        except FileExistsError:
            count = 1

        if os.path.exists(directory + filename + ".csv"):
            continue

        df = data[key].generatePandasDf()
        df.to_csv(directory + filename + ".csv", sep=',')

        # with open(directory + filename + '.json', 'w', encoding='utf-8') as f:
        #     json.dump(data[key].dict(), f, ensure_ascii=False, indent=4)
    return True
