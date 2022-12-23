from backend.model.baseModel import CustomBaseModel


class TrailingStopLossDataType(CustomBaseModel):
    base_move: float = -1
    base_stoploss: float = -1
    subsequent_move: float = -1
    subsequent_stoploss_increment: float = -1
    subsequent_stoploss_increment_change: float = -1
    final_minimum_stoploss: float = -1
