from datetime import datetime, timedelta
import threading
import requests
import time

MAX_THREADS = 1

START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2020, 12, 31)

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

total_days = (END_DATE - START_DATE).days + 1
DAYS_PER_THREAD = int(total_days/MAX_THREADS)

URL = "http://localhost:8001/intraday/"
BODY = strategyJson


def getRequest(index: int, output: list):
    start_date = START_DATE + timedelta(days=index * DAYS_PER_THREAD)
    end_date = START_DATE + \
        timedelta(days=(index + 1) * DAYS_PER_THREAD -
                  1) if index != MAX_THREADS - 1 else END_DATE
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
while index < MAX_THREADS:
    process = threading.Thread(target=getRequest, args=(index, output,))
    threadPool.append(process)
    process.start()
    index = index + 1

while len(threadPool) != 0:
    thread = threadPool.pop()
    thread.join()

end = time.time()


total_failed = 0
average_time = 0.0
max_time = 0
for entry in output:
    if entry["status_code"] != 200:
        total_failed = total_failed + 1

    average_time = average_time + entry["time"]/MAX_THREADS

    if max_time < entry["time"]:
        max_time = entry["time"]

print("")
print("")
print("")
print("----------------  Report  -----------------")
print(f'# Total Failed Percent - {total_failed*100/MAX_THREADS}')
print(f'# Average Request Time - {average_time} ms')
print(f'# Max Request Time - {max_time} ms')
print(f'# Total Time - {end - start} seconds')


print("done")
