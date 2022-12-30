from backend_process.model.candleStick import CandleStickDataType
from backend_process.model.strategy import StrategyDataType, ExitConditionDataSourceEnum
from backend_process.model.trade import TradeDataType


def checkIfTrailingStopLossHit(tradeData: TradeDataType, strategy: StrategyDataType) -> bool:
    if strategy.exit.trailing_stoploss == None:
        return False

    if strategy.exit.data_source == ExitConditionDataSourceEnum.PNL_POINTS:
        stoploss = getTrailingStoplossWrtPnlPoints(tradeData, strategy)
        if stoploss <= 0:
            return False

        currentPnl = tradeData.pnl[len(tradeData.pnl) - 1].points

        if currentPnl <= stoploss:
            return True

        return False

    if strategy.exit.data_source == ExitConditionDataSourceEnum.UNDERLYING_POINTS:
        stoploss = getTrailingStoplossWrtUnderlyingPoints(tradeData, strategy)
        if stoploss <= 0:
            return False

        currentOpen = tradeData.underlying_data[len(tradeData.pnl) - 1]

        if currentOpen <= stoploss:
            return True

        return False


def getTrailingStoplossWrtPnlPoints(tradeData: TradeDataType, strategy: StrategyDataType) -> float:
    max_pnl = 0
    base_trailing_enabled = False
    subsequent_trailing_enabled = False
    stoploss = 0
    target = 0
    trailing_hit_count = 0
    current_increment = 0

    if not strategy.exit.trailing_stoploss.base_move <= 0:
        base_trailing_enabled = True

    if not strategy.exit.trailing_stoploss.subsequent_move <= 0:
        subsequent_trailing_enabled = True

    # leaving last data point as that is current data (in case current data is smaller than )
    # that should be included in the handler to check with current data for stoploss
    for pnl in tradeData.pnl[0:len(tradeData.pnl)-1]:
        if pnl.points <= 0:
            continue

        if pnl.points > max_pnl:
            max_pnl = pnl.points

    if max_pnl <= 0:
        return -1

    if base_trailing_enabled:
        if max_pnl < strategy.exit.trailing_stoploss.base_move:
            return 0

    while target < max_pnl:
        if base_trailing_enabled:
            if max_pnl >= strategy.exit.trailing_stoploss.base_move:
                target = strategy.exit.trailing_stoploss.base_move
                stoploss = strategy.exit.trailing_stoploss.base_stoploss
                base_trailing_enabled = False
                if max_pnl < target:
                    subsequent_trailing_enabled = False
            else:
                target = strategy.exit.trailing_stoploss.base_move
                stoploss = 0

        if subsequent_trailing_enabled and not base_trailing_enabled:
            if max_pnl >= target + strategy.exit.trailing_stoploss.subsequent_move*(trailing_hit_count+1):
                stoploss = stoploss + current_increment + \
                    strategy.exit.trailing_stoploss.subsequent_stoploss_increment
                current_increment = current_increment + \
                    strategy.exit.trailing_stoploss.subsequent_stoploss_increment_change
                trailing_hit_count = trailing_hit_count + 1
            else:
                subsequent_trailing_enabled = False

        if not subsequent_trailing_enabled and not base_trailing_enabled:
            break

    if subsequent_trailing_enabled:
        if max_pnl - strategy.exit.trailing_stoploss.final_minimum_stoploss < stoploss:
            stoploss = max_pnl - strategy.exit.trailing_stoploss.final_minimum_stoploss

    return stoploss


def getTrailingStoplossWrtUnderlyingPoints(tradeData: TradeDataType, strategy: StrategyDataType) -> float:
    max_underlying = 0
    base_trailing_enabled = False
    subsequent_trailing_enabled = False
    stoploss = 0
    target = 0
    trailing_hit_count = 0
    current_increment = 0

    if not strategy.exit.trailing_stoploss.base_move <= 0:
        base_trailing_enabled = True

    if not strategy.exit.trailing_stoploss.subsequent_move <= 0:
        subsequent_trailing_enabled = True

    # leaving last data point as that is current data (in case current data is smaller than )
    # that should be included in the handler to check with current data for stoploss
    for underlying in tradeData.underlying_data[0:len(tradeData.pnl)-1]:
        if tradeData.underlying_data[0] <= underlying:
            continue

        if underlying > max_underlying:
            max_underlying = underlying

    if max_underlying <= 0:
        return -1

    if base_trailing_enabled:
        if max_underlying < strategy.exit.trailing_stoploss.base_move:
            return 0

    while target < max_underlying:
        if base_trailing_enabled:
            if max_underlying >= strategy.exit.trailing_stoploss.base_move:
                target = strategy.exit.trailing_stoploss.base_move
                stoploss = strategy.exit.trailing_stoploss.base_stoploss
                base_trailing_enabled = False
                if max_underlying < target:
                    subsequent_trailing_enabled = False

        if subsequent_trailing_enabled:
            if max_underlying >= target + strategy.exit.trailing_stoploss.subsequent_move*(trailing_hit_count+1):
                stoploss = stoploss + current_increment + \
                    strategy.exit.trailing_stoploss.subsequent_stoploss_increment
                current_increment = current_increment + \
                    strategy.exit.trailing_stoploss.subsequent_stoploss_increment_change
                trailing_hit_count = trailing_hit_count + 1
            else:
                subsequent_trailing_enabled = False

        if not subsequent_trailing_enabled and not base_trailing_enabled:
            break

    if subsequent_trailing_enabled:
        if max_underlying - strategy.exit.trailing_stoploss.final_minimum_stoploss < stoploss:
            stoploss = max_underlying - strategy.exit.trailing_stoploss.final_minimum_stoploss

    return stoploss
