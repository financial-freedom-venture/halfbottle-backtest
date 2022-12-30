from datetime import datetime, timedelta
import threading
import requests
import time

MAX_THREADS = 50

START_DATE = datetime(2019, 1, 1)
END_DATE = datetime(2019, 1, 1)

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
                "order_side": "sell",
                "contract_type": "call",
                "stoploss_percent": 40
            },
            {
                "strike":  {"strike_type": "ATM_AND_STRIKE_POINTS", "value": "ATM+0"},
                "order_side": "sell",
                "contract_type": "put",
                "stoploss_percent": 40
            }
        ]
    }
}

total_days = (END_DATE - START_DATE).days + 1
if total_days < MAX_THREADS:
    MAX_THREADS = total_days

DAYS_PER_THREAD = int(total_days/MAX_THREADS)


URL = "http://localhost:8001/intraday/"
BODY = strategyJson


def getRequest(start_date: datetime, end_date: datetime, output: list):
    params = {
        "start_date_day": start_date.day,
        "start_date_month": start_date.month,
        "start_date_year": start_date.year,

        "end_date_day": end_date.day,
        "end_date_month": end_date.month,
        "end_date_year": end_date.year
    }
    start_time = datetime.now()
    entry = {}
    response = requests.post(url=URL, json=BODY, params=params)

    end_time = datetime.now()
    entry["status_code"] = response.status_code
    entry["time"] = float((end_time - start_time).microseconds/1000)
    try:
        entry["data"] = response.json()
    except Exception as e:
        entry["error"] = e
    output.append(entry)


start = time.time()
output = []
index = 0
threadPool: list[threading.Thread] = []
currentDate = START_DATE
total_days_left = total_days
while index < MAX_THREADS:
    days_per_thread = int(total_days_left/(MAX_THREADS - index))
    end_date = currentDate + \
        timedelta(days=days_per_thread - 1)
    if end_date > END_DATE:
        end_date = END_DATE
    process = threading.Thread(
        target=getRequest, args=(currentDate, end_date, output,))
    threadPool.append(process)
    process.start()
    index = index + 1
    total_days_left = total_days_left - days_per_thread
    currentDate = end_date + timedelta(days=1)

while len(threadPool) != 0:
    thread = threadPool.pop()
    thread.join()

end = time.time()


total_failed = 0
average_time = 0.0
max_time = 0
tradeOutput = {}
for entry in output:
    if entry["status_code"] != 200:
        total_failed = total_failed + 1
        continue

    for key in entry["data"].keys():
        if key in tradeOutput.keys():
            tradeOutput[key] = tradeOutput[key] + entry["data"][key]
        else:
            tradeOutput[key] = entry["data"][key]

    average_time = average_time + entry["time"]/MAX_THREADS

    if max_time < entry["time"]:
        max_time = entry["time"]

print("")
print("")
print("")
print("---------------- Timing Report  -----------------")
print(f'# Total Failed Percent - {total_failed*100/MAX_THREADS}')
print(f'# Average Request Time - {average_time} ms')
print(f'# Max Request Time - {max_time} ms')
print(f'# Total Time - {end - start} seconds')

print()
print()

print("---------------- Trade Report  -----------------")
print(tradeOutput)
print()
print()

print("done")
