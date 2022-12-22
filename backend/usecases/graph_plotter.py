
from datetime import datetime
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.models.candleStick import CandleStickDataType
import pandas as pd
import plotly.graph_objects as go


def draw_option_chart_by_strike(HistoricalDataService: HistoricalDataService, date: datetime, ticker: str, strike: int, contract_type: str):
    dailyData = HistoricalDataService.getDailyData(date)
    filteredData = HistoricalDataService.filterDailyData(
        dailyData, [ticker+"wk"+str(int(strike))+contract_type.lower()])
    if len(filteredData) == 0:
        print("No Data Found")
        return

    tempTicker = ticker+"wk" + str(int(strike))+contract_type.lower()
    plotPnlGraph(filteredData[tempTicker], date, tempTicker)
    return


def draw_option_chart_by_ticker(HistoricalDataService: HistoricalDataService, date: datetime, ticker: str):
    dailyData = HistoricalDataService.getDailyData(date)
    filteredData = HistoricalDataService.filterDailyData(dailyData, [ticker])
    if len(filteredData) == 0:
        print("No Data Found")
        return

    plotPnlGraph(filteredData[ticker], date, ticker)
    return


def plotPnlGraph(candleStickList: dict[int, CandleStickDataType], date: datetime, ticker: str):
    candleTimestamp = [key for key in candleStickList.keys()]
    candleTimestamp.sort(reverse=False)
    data = [
        [
            candleStickList[timestamp].open,
            candleStickList[timestamp].high,
            candleStickList[timestamp].low,
            candleStickList[timestamp].close,
            str(datetime.fromtimestamp(candleStickList[timestamp].timestamp).hour) + ":" +
            str(datetime.fromtimestamp(
                candleStickList[timestamp].timestamp).minute)
        ] for timestamp in candleTimestamp]

    # Create the pandas DataFrame
    df = pd.DataFrame(data, columns=['open', 'high', 'low', 'close', 'time'])
    layout = go.Layout(title="Ticker - " + ticker +
                       f'\t Date - {date.isoformat()}')
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df['time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        ],
        layout=layout
    )

    fig.show()
    return
