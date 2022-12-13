from backtest_api.models.strategy import StrategyDataType
from backtest_api.models.trade import TradeReportDataType
import os.path
import csv


def __generateCsvRow(tradeReport: TradeReportDataType, strategy: StrategyDataType, start_date: str, end_date: str) -> list:
    # Discussed Columns
    # Strategy Columns - Start Date, End Date, Strategy Name, Underlying, Entry Time, Exit Time, CE Strike, PE Strike,
    # Result Columns - Total Points Captured, Total Trades Executed, Total Won Points, Total Winner Trades, Max Winner Points, Total Lost Points, Total Loser Trades, Max Loser Trades
    ce_strike = pe_strike = "ATM"
    stoploss = 0.0
    for spreadOrder in strategy.spread.order:
        if spreadOrder.contract_type.lower().strip() == "ce":
            ce_strike = spreadOrder.strike
            stoploss = stoploss + spreadOrder.stoploss_percent / \
                len(strategy.spread.order)
        if spreadOrder.contract_type.lower().strip() == "pe":
            pe_strike = spreadOrder.strike
            stoploss = stoploss + spreadOrder.stoploss_percent / \
                len(strategy.spread.order)

    output = []

    # Strategy Columns
    output.append(start_date)
    output.append(end_date)
    output.append(strategy.spread.spread_name)
    output.append(strategy.ticker)
    output.append(strategy.entry.time)
    output.append(strategy.exit.time)
    output.append(stoploss)
    output.append(ce_strike)
    output.append(pe_strike)

    # Result Columns
    output.append(tradeReport.total_points_captured)
    output.append(tradeReport.total_trades)
    output.append(tradeReport.total_won_points)
    output.append(tradeReport.total_won_trades)
    output.append(tradeReport.max_won_point)
    output.append(tradeReport.total_lost_points)
    output.append(tradeReport.total_lost_trades)
    output.append(tradeReport.max_lost_point)

    return output


def updateCsv(filename: str, tradeReport: TradeReportDataType, strategy: StrategyDataType, start_date: str, end_date: str):
    new_row = __generateCsvRow(tradeReport, strategy, start_date, end_date)
    __appendCsvRows(filename, new_row)
    return


def __appendCsvRows(filename: str, row: list):
    if os.path.isfile(filename):
        with open(filename, 'a') as fd:
            writer_object = csv.writer(fd)
            writer_object.writerow(row)
            fd.close()
    else:
        print(f'\n\n----------------- Error ------------------')
        print(f'\t file with filename- {filename} don\'t exist')
    return

def generateExcel