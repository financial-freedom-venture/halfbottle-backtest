

from backend.models.baseModel import CustomBaseModel


class CandleStickDataType(CustomBaseModel):
    ticker: str
    open: float
    high: float
    low: float
    close: float
    timestamp: int
    volume: int
    open_interest: int
