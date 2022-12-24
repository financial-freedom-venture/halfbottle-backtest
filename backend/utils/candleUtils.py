
from backend.model.candleStick import CandleStickDataType, CandleStickDictDataType, CandleStickListDataType


def convertFastAccessData(slowCandleData: dict[str, CandleStickListDataType]) -> dict[str, CandleStickDictDataType]:
    output: dict[str, CandleStickDictDataType] = {}
    for key in slowCandleData.keys():
        output[key] = CandleStickDictDataType(data={})
        for candleData in slowCandleData[key].data:
            output[key].data[candleData.timestamp] = candleData

    return output


def getMostRecentCandle(timestamp: int, candleData: dict[str, CandleStickDictDataType]) -> dict[str, CandleStickDataType]:
    output = {}
    for ticker in candleData.keys():
        if timestamp in candleData[ticker].data.keys():
            output[ticker] = candleData[ticker].data[timestamp]
        else:
            lastAvailableTimestamp = -1
            candleTimestamp = [
                key for key in candleData[ticker].data.keys()]
            candleTimestamp.sort(reverse=False)
            # first get old candle
            for tempTimestamp in candleTimestamp:
                if tempTimestamp < timestamp:
                    lastAvailableTimestamp = tempTimestamp
            if lastAvailableTimestamp != -1:
                output[ticker] = candleData[ticker].data[lastAvailableTimestamp]

            # then try new candle
            for index in range(0, len(candleTimestamp)):
                if candleTimestamp[len(candleTimestamp) - 1 - index] > timestamp:
                    lastAvailableTimestamp = candleTimestamp[len(
                        candleTimestamp) - 1 - index]
            if lastAvailableTimestamp != -1:
                output[ticker] = candleData[ticker].data[lastAvailableTimestamp]

    return output
