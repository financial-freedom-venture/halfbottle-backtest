from datetime import datetime
import threading
import requests
import time

MAX_THREADS = 1
TOTAL_REQUEST = 1


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

URL = "http://localhost:8001/intraday/"
PARAMS = {
    "date_day": 1,
    "date_month": 1,
    "date_year": 2020
}
BODY = strategyJson


def getRequest(output: list):
    start_time = datetime.now()
    entry = {}
    response = requests.post(url=URL, json=BODY, params=PARAMS)

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
while index < TOTAL_REQUEST:
    if len(threadPool) < MAX_THREADS:
        process = threading.Thread(target=getRequest, args=(output,))
        threadPool.append(process)
        process.start()
        index = index + 1
    else:
        while len(threadPool) != 0:
            thread = threadPool.pop()
            thread.join()
        print(f'# Percent Complete - {index*100/TOTAL_REQUEST}')

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

    average_time = average_time + entry["time"]/TOTAL_REQUEST

    if max_time < entry["time"]:
        max_time = entry["time"]

print("")
print("")
print("")
print("----------------  Report  -----------------")
print(f'# Total Failed Percent - {total_failed*100/TOTAL_REQUEST}')
print(f'# Average Request Time - {average_time} ms')
print(f'# Max Request Time - {max_time} ms')
print(f'# Total Time - {end - start} seconds')


print("done")
