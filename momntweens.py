from time import sleep
import requests
from datetime import datetime
import hmac
import hashlib
import configparser


def save_log(filename, data_string):
    my_date = datetime.now()
    form = my_date.isoformat()
    file = open("{}.txt".format(filename), "a")

    file.write(str(form) + "\n" + str(data_string) + "\n")

    file.close()


def get_system_status():
    api_endpoint = "https://api.wazirx.com/sapi/v1/systemStatus"
    response = requests.get(api_endpoint)
    json_data = response.json()
    if json_data and 'status' in json_data:
        status = json_data.get("status")
        if status == "normal":
            return True
    else:
        return False


def get_server_time():
    api_endpoint = "https://api.wazirx.com/sapi/v1/time"
    response = requests.get(api_endpoint)
    json_data = response.json()
    if json_data and 'serverTime' in json_data:
        svtime = json_data.get("serverTime")
        return(svtime)


def hashing(query_string):
    return hmac.new(
        SECRET_KEY.encode(
            "utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_wallet_bal(this_ticker, func):
    this_time = get_server_time()
    sleep(1)
    hashing_string = "recvWindow=20000&timestamp={}".format(this_time)
    this_signature = hashing(hashing_string)
    api_endpoint = "https://api.wazirx.com/sapi/v1/funds?recvWindow=20000&timestamp={}&signature={}".format(
        this_time, this_signature)
    headers = {'X-API-KEY': API_KEY}
    response = requests.get(api_endpoint, headers=headers)
    jason_data = response.json()
    for i in jason_data:
        ticker = i.get("asset")
        # print(ticker)
        if func == "free":
            if ticker == this_ticker:
                balance = i.get("free")
                return balance
        elif func == "locked":
            if ticker == this_ticker:
                balance = i.get("locked")
                return balance


def get_current_price(this_ticker):
    api_endpoint = 'https://api.wazirx.com/sapi/v1/ticker/24hr?symbol={}'.format(
        this_ticker)
    response = requests.get(api_endpoint)
    print(response.json())


def buy_busd():

    ticker = "busdusdt"
    try_no = 1
    price = LT
    while try_no <= 3:
        try:

            usdt_bal = float(get_wallet_bal("usdt", "free"))
            if usdt_bal < 2:
                save_log("buy_log", "usdt balance is low")
                return False

            quantity = usdt_bal / price - 1

            this_time = get_server_time()
            sleep(1)
            hash_string = "symbol={}&side=buy&type=limit&quantity={}&price={}&recvWindow=7000&timestamp={}".format(
                ticker, quantity, price, this_time)
            this_signature = hashing(hash_string)
            api_endpoint = 'https://api.wazirx.com/sapi/v1/order/'
            headers = {'X-API-KEY': API_KEY,
                       'Content-Type': 'application/x-www-form-urlencoded'}
            data = "symbol={}&side=buy&type=limit&quantity={}&price={}&recvWindow=7000&timestamp={}&signature={}".format(
                ticker, quantity, price, this_time, this_signature)
            response = requests.post(api_endpoint, headers=headers, data=data)
            print(response.json())
            data_string = response.json()
            save_log("buy_log", data_string)
            save_log("closed_orders", data_string)

            print(data)

            try_no = 1
            return True

        except Exception as e:
            msg = "tries: {}, error: {}".format(try_no, e)
            save_log("buy_log", msg)
            try_no = try_no+1
            sleep(3)
    return False


def sell_busd():
    sleep(1)
    ticker = "busdusdt"
    try_no = 1
    price = UT
    while try_no <= 3:
        try:
            usdc_bal = float(get_wallet_bal("busd", "free"))
            if usdc_bal < 2:
                save_log("sell_log", "busd balance is low")
                return False

            quantity = usdc_bal / price - 1

            this_time = get_server_time()
            sleep(1)
            hash_string = "symbol={}&side=sell&type=limit&quantity={}&price={}&recvWindow=7000&timestamp={}".format(
                ticker, quantity, price, this_time)
            this_signature = hashing(hash_string)
            api_endpoint = 'https://api.wazirx.com/sapi/v1/order/'
            headers = {'X-API-KEY': API_KEY,
                       'Content-Type': 'application/x-www-form-urlencoded'}
            data = "symbol={}&side=sell&type=limit&quantity={}&price={}&recvWindow=7000&timestamp={}&signature={}".format(
                ticker, quantity, price, this_time, this_signature)
            response = requests.post(api_endpoint, headers=headers, data=data)
            print(response.json())
            data_string = response.json()
            save_log("sell_log", data_string)
            save_log("closed_orders", data_string)

            # print(data)

            try_no = 1
            return True

        except Exception as e:
            msg = "tries: {}, error: {}".format(try_no, e)
            save_log("buy_log", msg)
            try_no = try_no+1
            sleep(3)
    return True


while True:
    # Read config.ini file
    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")
    secretinfo = config_obj["secret_info"]
    priceinfo = config_obj["price_info"]

    # Get info from config file
    LT = float(priceinfo["buy_price"])
    UT = float(priceinfo["sell_price"])
    API_KEY = secretinfo["api_key"]
    SECRET_KEY = secretinfo["secret_key"]

    save_log("service_log", "service online")
    buy_busd()
    sell_busd()
    save_log("service_log", "cycle completed")
    sleep(3)
