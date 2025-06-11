from kiteconnect import KiteConnect
import json
import time
import pandas as pd

API_KEY = "your_api_key_here"        # Replace with your API Key

def load_token():
    with open("token.json", "r") as f:
        token_data = json.load(f)
    return token_data["access_token"]

def get_instrument_tokens(kite, symbol="NIFTY", expiry=None):
    # Fetch NSE instruments
    instruments = kite.instruments("NSE")
    tokens = []
    for inst in instruments:
        if symbol in inst["tradingsymbol"] and inst["instrument_type"] == "CE":
            if expiry is None or expiry in inst["expiry"]:
                tokens.append(inst["instrument_token"])
    return tokens

def fetch_option_data(kite, tokens):
    data = kite.ltp(["NSE:" + str(token) for token in tokens])
    return data

def main():
    access_token = load_token()
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(access_token)

    expiry = None  # You can filter expiry like "2025-06-18"

    while True:
        try:
            tokens = get_instrument_tokens(kite, expiry=expiry)
            option_data = fetch_option_data(kite, tokens)
            df = pd.DataFrame.from_dict(option_data, orient='index')
            print(df.head())
            # Save or push this data wherever needed
            time.sleep(120)  # 2 min interval
        except Exception as e:
            print("Error fetching live data:", e)
            time.sleep(60)

if __name__ == "__main__":
    main()
