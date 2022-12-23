from datetime import datetime, timedelta
from typing import Optional, Tuple
from backend.model.baseModel import CustomBaseModel
from backend.model.candleStick import ContractTypeEnum, ExpiryTypeEnum
from backend.model.error import ErrorCodeEnum, ErrorResponse
import pandas as pd
from pathlib import Path


class AvailableOptionsExpiryData(CustomBaseModel):
    weekly_expiry_data: dict[datetime, dict[datetime, list[str]]]
    monthly_expiry_data: dict[datetime, dict[datetime, list[str]]]


class AvailableCsvData(CustomBaseModel):
    cash: dict[str, list[datetime]]
    options: dict[str, AvailableOptionsExpiryData]


class CsvDataStore:
    def __init__(self, data_path: str) -> None:
        self.DATA_PATH = data_path
        self.availableData = self.__generateAvailableData(data_path)
        return

    def __generateAvailableData(self, data_path: str) -> AvailableCsvData:
        last_folder = data_path.removesuffix(
            "/").split("/")[len(data_path.removesuffix("/").split("/")) - 1]
        files = list(Path(data_path).rglob("*.[cC][sS][vV]"))
        availableData = AvailableCsvData(cash={}, options={})
        for file in files:
            filepath = ("/" + "/".join(file.parts)).replace("//", "/")
            forward_path = filepath.split(
                "/" + last_folder + "/")[len(filepath.split("/" + last_folder + "/")) - 1]
            parts = forward_path.split("/")

            if parts[0].upper() == "CASH":
                if parts[1] in availableData.cash.keys():
                    date_str = parts[2].removesuffix(".csv")
                    availableData.cash[parts[1]].append(datetime(
                        int(date_str.split("-")[0]), int(date_str.split("-")[1]), int(date_str.split("-")[2])))
                else:
                    date_str = parts[2].removesuffix(".csv")
                    availableData.cash[parts[1]] = [datetime(
                        int(date_str.split("-")[0]), int(date_str.split("-")[1]), int(date_str.split("-")[2]))]
            elif parts[0].upper() == "OPTIONS":
                if parts[1] in availableData.options.keys():

                    expiry_date_str = parts[3].split("->>")[1]
                    expiry_date = datetime(int(expiry_date_str.split(
                        "-")[0]), int(expiry_date_str.split("-")[1]), int(expiry_date_str.split("-")[2]))

                    data_date_str = parts[4].removesuffix(".csv")
                    data_date = datetime(
                        int(data_date_str.split("-")[0]), int(data_date_str.split("-")[1]), int(data_date_str.split("-")[2]))
                    if parts[2] == "WEEKLY":
                        if expiry_date in availableData.options[parts[1]].weekly_expiry_data.keys():
                            if data_date in availableData.options[parts[1]
                                                                  ].weekly_expiry_data[expiry_date].keys():
                                availableData.options[parts[1]
                                                      ].weekly_expiry_data[expiry_date][data_date].append(parts[5].removesuffix(".csv"))
                            else:
                                availableData.options[parts[1]
                                                      ].weekly_expiry_data[expiry_date][data_date] = [parts[5].removesuffix(".csv")]
                        else:
                            availableData.options[parts[1]
                                                  ].weekly_expiry_data[expiry_date] = {}
                            availableData.options[parts[1]
                                                  ].weekly_expiry_data[expiry_date][data_date] = [parts[5].removesuffix(".csv")]
                    elif parts[2] == "MONTHLY":
                        if expiry_date in availableData.options[parts[1]].monthly_expiry_data.keys():
                            if data_date in availableData.options[parts[1]
                                                                  ].monthly_expiry_data[expiry_date].keys():
                                availableData.options[parts[1]
                                                      ].monthly_expiry_data[expiry_date][data_date].append(parts[5].removesuffix(".csv"))
                            else:
                                availableData.options[parts[1]
                                                      ].monthly_expiry_data[expiry_date][data_date] = [parts[5].removesuffix(".csv")]
                        else:
                            availableData.options[parts[1]
                                                  ].monthly_expiry_data[expiry_date] = {}
                            availableData.options[parts[1]
                                                  ].monthly_expiry_data[expiry_date][data_date] = [parts[5].removesuffix(".csv")]
                else:
                    availableData.options[parts[1]
                                          ] = AvailableOptionsExpiryData(weekly_expiry_data={}, monthly_expiry_data={})

                    if parts[2] == "WEEKLY":
                        expiry_date_str = parts[3].split("->>")[1]
                        expiry_date = datetime(int(expiry_date_str.split(
                            "-")[0]), int(expiry_date_str.split("-")[1]), int(expiry_date_str.split("-")[2]))

                        data_date_str = parts[4].removesuffix(".csv")
                        data_date = datetime(
                            int(data_date_str.split("-")[0]), int(data_date_str.split("-")[1]), int(data_date_str.split("-")[2]))

                        availableData.options[parts[1]
                                              ].weekly_expiry_data[expiry_date] = {}
                        availableData.options[parts[1]
                                              ].weekly_expiry_data[expiry_date][data_date] = [parts[5].removesuffix(".csv")]
                    elif parts[2] == "MONTHLY":
                        expiry_date_str = parts[3].split("->>")[1]
                        expiry_date = datetime(int(expiry_date_str.split(
                            "-")[0]), int(expiry_date_str.split("-")[1]), int(expiry_date_str.split("-")[2]))

                        data_date_str = parts[2].removesuffix(".csv")
                        data_date = datetime(
                            int(data_date_str.split("-")[0]), int(data_date_str.split("-")[1]), int(data_date_str.split("-")[2]))
                        availableData.options[parts[1]
                                              ].monthly_expiry_data[expiry_date] = {}
                        availableData.options[parts[1]
                                              ].monthly_expiry_data[expiry_date][data_date] = [parts[5].removesuffix(".csv")]

        return availableData

    def getCashData(self, ticker: str, date: datetime) -> Tuple[Optional[pd.DataFrame], Optional[ErrorResponse]]:
        path = self.DATA_PATH + "/CASH/" + ticker.upper() + "/" + \
            date.isoformat().split("T")[0] + '.csv'
        path = path.replace("//", "/")

        backupDate = str(int(date.isoformat().split("T")[0].split("-")[0])) + "-" + str(int(date.isoformat(
        ).split("T")[0].split("-")[1])) + "-" + str(int(date.isoformat().split("T")[0].split("-")[2]))
        backupPath = self.DATA_PATH + "/CASH/" + ticker.upper() + "/" + \
            backupDate + '.csv'
        backupPath = backupPath.replace("//", "/")

        try:
            df = pd.read_csv(path)
            return df, None
        except Exception as e:
            try:
                df = pd.read_csv(backupPath)
                return df, None
            except Exception as e:
                print(
                    f"CsvDataStore: Data Not Found Ticker - {ticker}, Date - {backupDate}")
                print(e)
                return None, ErrorResponse(
                    error_code=ErrorCodeEnum.NO_DATA,
                    message=f"CsvDataStore: Data Not Found Ticker - {ticker}, Date - {backupDate}"
                )

    def getOptionsData(self, ticker: str, expiry_type: ExpiryTypeEnum, strike: int, contract_type: ContractTypeEnum, date: datetime) -> Tuple[Optional[pd.DataFrame], Optional[ErrorResponse]]:
        expiry = self.getExpiryDate(ticker, expiry_type, date)
        if expiry == None:
            return None, ErrorResponse(
                error_code=ErrorCodeEnum.NO_DATA,
                message=f"CsvDataStore: Options Data Not Found Ticker - {ticker}, expiry_type - {expiry_type}, expiry - {formattedExpiryDate}, contract_type - {contract_type}, Date - {formattedDate}"
            )

        formattedExpiryDate = str(int(expiry.isoformat().split("T")[0].split("-")[0])) + "-" + str(int(expiry.isoformat(
        ).split("T")[0].split("-")[1])) + "-" + str(int(expiry.isoformat().split("T")[0].split("-")[2]))

        formattedDate = str(int(date.isoformat().split("T")[0].split("-")[0])) + "-" + str(int(date.isoformat(
        ).split("T")[0].split("-")[1])) + "-" + str(int(date.isoformat().split("T")[0].split("-")[2]))

        path = self.DATA_PATH + "/OPTIONS/" + ticker.upper() + "/" + \
            expiry_type.upper() + '/' + \
            "EXPIRY->>" + formattedExpiryDate + '/' + \
            formattedDate + '/' + \
            str(strike) + '-' + contract_type.upper() + '.csv'
        path = path.replace("//", "/")

        try:
            df = pd.read_csv(path)
            return df, None
        except Exception as e:
            print(
                f"CsvDataStore: Options Data Not Found Ticker - {ticker}, expiry_type - {expiry_type}, expiry - {formattedExpiryDate}, contract_type - {contract_type}, Date - {formattedDate}")
            print(e)
            return None, ErrorResponse(
                error_code=ErrorCodeEnum.NO_DATA,
                message=f"CsvDataStore: Options Data Not Found Ticker - {ticker}, expiry_type - {expiry_type}, expiry - {formattedExpiryDate}, contract_type - {contract_type}, Date - {formattedDate}"
            )

    def getExpiryDate(self, ticker: str, expiry_type: ExpiryTypeEnum, date: datetime) -> Optional[datetime]:
        if expiry_type == ExpiryTypeEnum.MONTHLY:
            availableExpiry = list(self.availableData.options[ticker.upper()].monthly_expiry_data.keys(
            )).sort(key=lambda x: x.timestamp(), reverse=False)
            date_index = -1
            for index in range(0, len(availableExpiry)):
                if availableExpiry[index] >= date:
                    date_index = index
                    break

            if date_index == -1:
                return None

            if availableExpiry[date_index].month == date.month:
                return availableExpiry[date_index]

            if date_index == 0:
                return None

            if availableExpiry[date_index - 1].month == date.month and availableExpiry[date_index].month == (date + timedelta(days=32)).month:
                return availableExpiry[date_index]

        else:
            availableExpiry = list(self.availableData.options[ticker.upper()].weekly_expiry_data.keys(
            ))
            availableExpiry.sort(
                key=lambda x: x.timestamp(), reverse=False)
            date_index = -1
            for index in range(0, len(availableExpiry)):
                if availableExpiry[index] >= date:
                    date_index = index
                    break

            if date_index == -1:
                return None

            if availableExpiry[date_index].isocalendar()[1] == date.isocalendar()[1]:
                return availableExpiry[date_index]

            if date_index == 0:
                return None

            if availableExpiry[date_index - 1].isocalendar()[1] == date.isocalendar()[1] and availableExpiry[date_index].isocalendar()[1] == (date + timedelta(days=7)).isocalendar()[1]:
                return availableExpiry[date_index]

        return None
