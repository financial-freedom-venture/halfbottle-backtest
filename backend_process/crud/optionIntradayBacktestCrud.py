from datetime import datetime, timedelta
from typing import Optional, Union
from model.strategy import StrategyDataType
from model.trade import TradeDataType, TradeDetailedDataType, TradeOutputEnum, TradeReportDataType
from backend_process.usecase.strategy_tester import StrategyBackTester


class IntradayBackTesterCrud:

    def __init__(self, strategyTesterService: StrategyBackTester) -> None:
        self.strategyTesterService = strategyTesterService
        return

    def testStrategy(self, start_date: datetime, end_date: datetime, strategy: StrategyDataType, detailedReport: bool = False) -> Union[TradeReportDataType, TradeDetailedDataType, None]:
        tradeDataList = []

        currentDate = start_date
        while end_date >= currentDate:
            tradeData = self.strategyTesterService.testStrategy(
                currentDate, strategy)
            if tradeData != None:
                tradeDataList.append(tradeData)
            currentDate = currentDate + timedelta(days=1)

        if detailedReport:
            return TradeDetailedDataType(tradeData=tradeDataList)
        return self.generateTradeReport(tradeDataList)

    def generateTradeReport(self, tradesData: list[TradeDataType]) -> TradeReportDataType:
        totalROI = 0
        totalWinners = 0
        totalLosers = 0
        maxWinner = 0
        maxLoser = 0
        totalWinPoints = 0
        totalLostPoints = 0
        for tradeData in tradesData:

            totalROI = totalROI + tradeData.pnl[len(tradeData.pnl) - 1].points
            # averagePoints = totalROI / len(tradesData)
            if tradeData.trade_output == TradeOutputEnum.WINNER:
                totalWinPoints = totalWinPoints + \
                    tradeData.pnl[len(tradeData.pnl) - 1].points
                totalWinners = totalWinners + 1
                # averageWinPoints = totalWinPoints / totalWinners
                if tradeData.pnl[len(tradeData.pnl) - 1].points > maxWinner:
                    maxWinner = tradeData.pnl[len(tradeData.pnl) - 1].points
            else:
                totalLostPoints = totalLostPoints + \
                    tradeData.pnl[len(tradeData.pnl) - 1].points
                totalLosers = totalLosers + 1
                # averageLostPoints = totalLostPoints / totalLosers
                if tradeData.pnl[len(tradeData.pnl) - 1].points < maxLoser:
                    maxLoser = tradeData.pnl[len(tradeData.pnl) - 1].points

        return TradeReportDataType(
            total_points_captured=totalROI,
            total_trades=len(tradesData),
            total_won_points=totalWinPoints,
            total_won_trades=totalWinners,
            # average_won_points = averageWinPoints,
            max_won_point=maxWinner,
            total_lost_points=totalLostPoints,
            total_lost_trades=totalLosers,
            max_lost_point=maxLoser
            # average_lost_point= averageLostPoints

        )
