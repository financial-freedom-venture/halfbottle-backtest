

from backend.model.strategy import SpreadOrderDataType, SpreadStrikeDataType


def getSpreadOrderStrike(ticker: str, underlying_value: float, strike: SpreadStrikeDataType) -> int:
    strike_str = int(strike.value.upper().removeprefix("ATM").strip(
    )) if strike.value.upper().removeprefix("ATM").strip() != "" else 0

    atm = getAtm(ticker, underlying_value)

    return atm + strike_str


def getAtm(ticker: str, price: float) -> int:
    if ticker.upper() == "NIFTY":
        return 50 * int((price + 25.0)/50.0)
    elif ticker.upper() == "CNXBAN":
        return 100 * int((price + 50.0)/100.0)


def getLotSize(ticker: str) -> int:
    if ticker.upper() == "NIFTY":
        return 50
    elif ticker.upper() == "CNXBAN":
        return 25
