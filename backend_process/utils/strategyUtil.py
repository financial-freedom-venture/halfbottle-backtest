

from model.strategy import SpreadOrderDataType, SpreadStrikeDataType, StrategyDataType


def getStrategyTickers(strategy: StrategyDataType, underlying_value: float) -> list[str]:
    output = []
    output.append(strategy.ticker.upper())
    for order in strategy.spread.order:
        strike = getSpreadOrderStrike(
            strategy.ticker, underlying_value, order.strike)

        if str(strike) + order.contract_type not in output:
            output.append(str(strike) + order.contract_type)

        if order.hedge_strike != None:
            hedge_strike = getSpreadOrderStrike(
                strategy.ticker, underlying_value, order.hedge_strike)

            if str(hedge_strike) + order.contract_type not in output:
                output.append(str(hedge_strike) + order.contract_type)

    return output


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
