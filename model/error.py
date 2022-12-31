from model.baseModel import CustomBaseModel
from typing import Union
from enum import Enum


class ErrorCodeEnum(str, Enum):
    # API End POINT ERROR CODES
    RESOURCE_NOT_AVAILABLE = "resource not available"
    INVALID_REQUEST = "invalid request"
    INVALID_SYMBOL = "invalid symbol"
    NO_DATA = "no_data"
    LIVE_DATA_NOT_SUPPORTED = "live data not supported"
    INVALID_TIMEFRAME = "invalid timeframe"
    USER_PERMISSION_INVALID = "user permission invalid"
    UNAUTHORIZED = "unauthorized"
    TOKEN_EXPIRED = "token expired"
    INTERNAL_SERVER_ERROR = "internal server error"
    INVALID_SOURCE = "invalid source"

    # Trading Bot Error Codes
    NO_ACTIVE_TRADE_AVAILABLE = "no active trade available"
    ERROR_IN_SAVING_CONFIG = "error in saving config"
    ERROR_IN_SAVING_CONTEXT = "error in saving context"
    ERROR_IN_SAVING_ACCOUNT_DETAILS = "error in saving account details"
    NOT_ENOUGH_MARGIN = "not enough margin"
    TRADING_BOT_INTERNAL_ERROR = "trading bot internal error"
    SYMBOL_NOT_EXIST_IN_CONFIG = "symbol not exist in config"
    MAX_ACTIVE_TRADE_LIMIT = "max active trade limit"
    # Trading Bot Error Codes
    STRATEGY_DOES_NOT_EXIST = "strategy does not exist"
    INVALID_STRATEGY = "invalid strategy"


class ErrorResponse(CustomBaseModel):
    message: str
    error_code: ErrorCodeEnum
