from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple
from backend.models.candleStick import CandleStickDataType
from backend.models.error import ErrorResponse

from backend.models.order import OrderDataType, OrderRequestDataType


class ExchangeServiceAbstract(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def checkExchangeActive(self) -> bool:
        return False

    @abstractmethod
    def getAvailableTickers(self, instrument: str) -> Tuple[list[str], Optional[ErrorResponse]]:
        return None, None

    @abstractmethod
    def getTradingFee(self, order: OrderDataType) -> Tuple[float, Optional[ErrorResponse]]:
        return None, None

    #################################
    # Order End points #
    #################################
    @abstractmethod
    def placeOrder(self, orderRequest: OrderRequestDataType) -> Tuple[Optional[OrderDataType], Optional[ErrorResponse]]:
        return None, None

    @abstractmethod
    def getOrder(self, orderId: int) -> Tuple[Optional[OrderDataType], Optional[ErrorResponse]]:
        return

    @abstractmethod
    def cancelOrder(self, orderId: int) -> Tuple[Optional[OrderDataType], Optional[bool]]:
        return

    @abstractmethod
    def getAllOpenOrders(self) -> Tuple[Optional[list[OrderDataType]], Optional[ErrorResponse]]:
        return

    @abstractmethod
    def squareOffPosition(self) -> Tuple[Optional[list[OrderDataType]], Optional[ErrorResponse]]:
        return

    #################################
    # Data End points #
    #################################

    @abstractmethod
    def getHistoricalData(
        self,
        tickers: list[str],
        startTime: datetime,
        endTime: datetime,
        timeFrame: TimeFrameEnum,
        index: bool = False
    ) -> Tuple[Optional[list[CandleStickDataType]], Optional[ErrorResponse]]:
        return False

    @abstractmethod
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

    @abstractmethod
    def getAccountDetails(self):
        return None, None

    #################################
    # Get Portfolio Details #
    #################################

    @abstractmethod
    def getPortfolioHoldings(self):
        return None, None

    @abstractmethod
    def getPortfolioPositions(self):
        return None, None
