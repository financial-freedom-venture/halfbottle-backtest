from datetime import datetime
from typing import Optional, Tuple
from backend.dataservice.exchange.exchangeService import ExchangeServiceAbstract
from backend.models.candleStick import CandleStickDataType
from backend.models.error import ErrorResponse

from backend.models.order import OrderDataType, OrderRequestDataType


class IciciExchangeService(ExchangeServiceAbstract):

    def __init__(self) -> None:
        super().__init__()

    def checkExchangeActive(self) -> bool:
        return False

    def getAvailableTickers(self, instrument: str) -> Tuple[list[str], Optional[ErrorResponse]]:
        return None, None

    def getTradingFee(self, order: OrderDataType) -> Tuple[float, Optional[ErrorResponse]]:
        return None, None

    #################################
    # Order End points #
    #################################
    def placeOrder(self, orderRequest: OrderRequestDataType) -> Tuple[Optional[OrderDataType], Optional[ErrorResponse]]:
        return None, None

    def getOrder(self, orderId: int) -> Tuple[Optional[OrderDataType], Optional[ErrorResponse]]:
        return

    def cancelOrder(self, orderId: int) -> Tuple[Optional[OrderDataType], Optional[bool]]:
        return

    def getAllOpenOrders(self) -> Tuple[Optional[list[OrderDataType]], Optional[ErrorResponse]]:
        return

    def squareOffPosition(self) -> Tuple[Optional[list[OrderDataType]], Optional[ErrorResponse]]:
        return

    #################################
    # Data End points #
    #################################
    def getHistoricalData(
        self,
        tickers: list[str],
        startTime: datetime,
        endTime: datetime,
        timeFrame: TimeFrameEnum,
        index: bool = False
    ) -> Tuple[Optional[list[CandleStickDataType]], Optional[ErrorResponse]]:
        return False

    def getLiveData(
        self,
        tickers: list[str],
        timeFrame: TimeFrameEnum,
        index: bool = False
    ) -> Tuple[Optional[list[CandleStickDataType]], Optional[ErrorResponse]]:
        return None, None

    #################################
    # Get Account Details #
    #################################
    def getAccountDetails(self):
        return None, None

    #################################
    # Get Portfolio Details #
    #################################
    def getPortfolioHoldings(self):
        return None, None

    def getPortfolioPositions(self):
        return None, None
