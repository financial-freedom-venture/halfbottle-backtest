import json
import breeze_connect
from datetime import datetime

api_key = "33H8u4b9XU8@v5955289vr7921781Mq9"
api_secret = "118(52~263%G269Kf5b(x24284E8108`"
api_session = "1940681"

icici_connection = breeze_connect.BreezeConnect(api_key)
icici_connection.generate_session(
    api_secret=api_secret, session_token=api_session)

data = icici_connection.get_historical_data(
    interval="1minute",
    from_date="2022-10-10T07:00:00.000Z",
    to_date="2022-10-10T07:00:00.000Z",
    stock_code="CNXBAN",
    exchange_code="NSE",
    product_type="other",
    expiry_date="",
    right="other",
    strike_price=""
)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# print(data)
