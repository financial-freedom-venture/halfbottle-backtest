
from backend.models.candleStick import CandleStickDataType, CandleStickDictDataType, CandleStickListDataType


def convertFastAccessData(slowCandleData: dict[str, CandleStickListDataType]) -> dict[str, CandleStickDictDataType]:
    output: dict[str, CandleStickDictDataType] = {}
    for key in slowCandleData.keys():
        output[key] = CandleStickDictDataType(data={})
        for candleData in slowCandleData[key].data:
            output[key].data[candleData.timestamp] = candleData

    return output


def getMostRecentCandle(tickers: list[str], timestamp: int, candleData: dict[str, CandleStickDictDataType]) -> dict[str, CandleStickDataType]:
    output = {}
    for ticker in tickers:
        output[ticker] = candleData[ticker].data[timestamp]
    return output
