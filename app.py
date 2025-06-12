import streamlit as st
from kiteconnect import KiteConnect
import pandas as pd
import datetime
from bs_calculator import bs_delta
from streamlit_autorefresh import st_autorefresh

# Load API credentials from Streamlit secrets
API_KEY = st.secrets["KiteConnect"]["api_key"]
ACCESS_TOKEN = st.secrets["KiteConnect"]["access_token"]

def get_kite_client():
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(ACCESS_TOKEN)
    return kite

def fetch_nifty_option_chain(kite):
    try:
        instruments = kite.instruments("NFO")
    except Exception as e:
        st.error(f"Error fetching instruments: {e}")
        return pd.DataFrame()

    today = datetime.date.today()
    option_data = [
        inst for inst in instruments
        if "NIFTY" in inst["name"]
        and inst["segment"] == "NFO-OPT"
        and inst["instrument_type"] in ["CE", "PE"]
        and inst["expiry"] >= today

    ]
    return pd.DataFrame(option_data)

def get_ltp(kite, tradingsymbols):
    try:
        response = kite.ltp(["NFO:" + ts for ts in tradingsymbols])
        return {k.split(":")[1]: v["last_price"] for k, v in response.items()}
    except Exception as e:
        st.warning(f"Error fetching LTPs: {e}")
        return {}

def calculate_delta(row, spot_price):
    try:
        K = row["strike"]
        T = (row["expiry"] - datetime.date.today()).days / 365
        r = 0.06  # risk-free rate
        sigma = 0.18  # estimated IV or fetch from live data
        option_type = "call" if row["instrument_type"] == "CE" else "put"
        return round(bs_delta(spot_price, K, T, r, sigma, option_type), 2)
    except:
        return None

def main():
    st.set_page_config(layout="wide")
    st.title("🔐 Nifty Iron Condor Dashboard")

    # Auto-refresh every 2 minutes
    st_autorefresh(interval=120000, key="datarefresh")

    try:
        kite = get_kite_client()
    except Exception as e:
        st.error(f"Error initializing KiteConnect client: {e}")
        return

    oc_df = fetch_nifty_option_chain(kite)
    if oc_df.empty:
        st.warning("No option chain data available.")
        return

    try:
        spot = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
    except Exception as e:
        st.error(f"Error fetching NIFTY spot price: {e}")
        return

    st.metric("📈 NIFTY Spot", round(spot, 2))

    # Filter near expiry options
    expiry = oc_df["expiry"].min()
    oc_df = oc_df[oc_df["expiry"] == expiry]

    # Select strikes near ATM (+-500)
    atm_range = 500
    oc_df = oc_df[
        (oc_df["strike"] > spot - atm_range) & (oc_df["strike"] < spot + atm_range)
    ]

    ts_list = oc_df["tradingsymbol"].tolist()
    ltp_map = get_ltp(kite, ts_list)
    oc_df["ltp"] = oc_df["tradingsymbol"].map(ltp_map)

    oc_df["delta"] = oc_df.apply(lambda row: calculate_delta(row, spot), axis=1)

    with st.expander("📊 Full Option Chain"):
        st.dataframe(
            oc_df[["tradingsymbol", "strike", "instrument_type", "ltp", "delta"]]
            .sort_values("strike")
            .reset_index(drop=True)
        )

    ce_candidates = oc_df[
        (oc_df["instrument_type"] == "CE") & (oc_df["delta"].between(0.12, 0.18))
    ].sort_values("strike")

    pe_candidates = oc_df[
        (oc_df["instrument_type"] == "PE") & (oc_df["delta"].between(-0.18, -0.12))
    ].sort_values("strike", ascending=False)

    st.subheader("🦾 Iron Condor Suggestion (±0.15 Delta)")

    if not ce_candidates.empty and not pe_candidates.empty:
        sell_ce = ce_candidates.iloc[0]
        sell_pe = pe_candidates.iloc[0]

        st.write(
            "🔹 **Sell CE**:", sell_ce["tradingsymbol"], "| Strike:", sell_ce["strike"], "| Δ:", sell_ce["delta"]
        )
        st.write(
            "🔹 **Sell PE**:", sell_pe["tradingsymbol"], "| Strike:", sell_pe["strike"], "| Δ:", sell_pe["delta"]
        )

        st.info("You can now manually sell these strikes and define wings based on your risk appetite.")
    else:
        st.warning("No strikes found with desired delta. Try widening the delta range.")

    st.caption("⏱ Auto-refreshing every 2 minutes...")

if __name__ == "__main__":
    main()
