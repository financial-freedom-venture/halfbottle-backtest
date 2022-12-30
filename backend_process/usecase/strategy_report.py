from backend_process.model.trade import TradeDataType, TradeOutputEnum, TradeReportDataType


def generateTradeReport(tradesData: list[TradeDataType]) -> TradeReportDataType:
    totalROI = 0
    totalWinners = 0
    totalLosers = 0
    maxWinner = 0
    maxLoser = 0
    totalWinPoints = 0
    totalLostPoints = 0
    for tradeData in tradesData:

        totalROI = totalROI + tradeData.pnl[len(tradeData.pnl) - 1].points

        if tradeData.trade_output == TradeOutputEnum.WINNER:
            totalWinPoints = totalWinPoints + \
                tradeData.pnl[len(tradeData.pnl) - 1].points
            totalWinners = totalWinners + 1
            if tradeData.pnl[len(tradeData.pnl) - 1].points > maxWinner:
                maxWinner = tradeData.pnl[len(tradeData.pnl) - 1].points
        else:
            totalLostPoints = totalLostPoints + \
                tradeData.pnl[len(tradeData.pnl) - 1].points
            totalLosers = totalLosers + 1
            if tradeData.pnl[len(tradeData.pnl) - 1].points < maxLoser:
                maxLoser = tradeData.pnl[len(tradeData.pnl) - 1].points

    return TradeReportDataType(
        total_points_captured=totalROI,
        total_trades=len(tradesData),
        total_won_points=totalWinPoints,
        total_won_trades=totalWinners,
        max_won_point=maxWinner,
        total_lost_points=totalLostPoints,
        total_lost_trades=totalLosers,
        max_lost_point=maxLoser

    )
