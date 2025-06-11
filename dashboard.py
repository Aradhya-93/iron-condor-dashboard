import streamlit as st
import pandas as pd
import json
from kiteconnect import KiteConnect

API_KEY = "your_api_key_here"

def load_token():
    with open("token.json", "r") as f:
        token_data = json.load(f)
    return token_data["access_token"]

def main():
    st.title("Nifty Iron Condor Dashboard")

    access_token = load_token()
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(access_token)

    st.write("Fetching live data...")

    try:
        instruments = kite.instruments("NSE")
        nifty_calls = [i for i in instruments if "NIFTY" in i["tradingsymbol"] and i["instrument_type"] == "CE"]
        df = pd.DataFrame(nifty_calls)
        st.dataframe(df.head(10))
    except Exception as e:
        st.error(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
