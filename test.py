
from datetime import datetime
from backend.crud.optionIntradayBacktestCrud import IntradayBackTesterCrud
from backend.dataservice.historical_dataservice import HistoricalDataService
from backend.models.strategy import StrategyDataType
from backend.usecases.strategy_tester import StrategyBackTester


strategyJson = {
    "ticker": "CNXBAN",
    "expiry": "weekly",
    "entry": {
        "included_days": [],
        "time": "13:30"
    },
    "exit": {
        "data_source": "pnl_points",
        "trailing_stoploss": {
            "base_move": -1,
            "base_stoploss": -1,
            "subsequent_move": -1,
            "subsequent_stoploss_increment": -1,
            "subsequent_stoploss_increment_change": -1,
            "final_minimum_stoploss": -1
        },
        "direction": "long",
        "take_profit": -1,
        "stoploss": -1,
        "time": "14:30"
    },
    "spread": {
        "spread_name": "Short Straddle",
        "stoploss_condition": "exit_one_leg",
        "order": [
            {
                "strike": {"strike_type": "ATM_AND_STRIKE_POINTS", "value": "ATM+0"},
                "order_side": "buy",
                "contract_type": "call",
                "stoploss_percent": 40
            },
            {
                "strike":  {"strike_type": "ATM_AND_STRIKE_POINTS", "value": "ATM+0"},
                "order_side": "buy",
                "contract_type": "put",
                "stoploss_percent": 40
            }
        ]
    }
}

URL = "https://backtest.halfbottle.in/intraday/"

params = {
    "day_date": 1,
    "day_month": 1,
    "day_year": 2020,
    "requestData": strategyJson
}

strategy = StrategyDataType(**strategyJson)

optionsDatastore = HistoricalDataService("http://localhost:7001/")
strategyBacktestingService = StrategyBackTester(optionsDatastore)
crud = IntradayBackTesterCrud(strategyBacktestingService)

data = crud.testStrategy(
    datetime(2020, 1, 1),
    strategy
)

print(data)
