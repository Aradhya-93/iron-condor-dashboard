import streamlit as st
import pandas as pd
import datetime as dt
import time
import numpy as np

# Simulated data fetching function (replace with real API logic)
@st.cache_data(ttl=120)
def fetch_option_data():
    now = dt.datetime.now()
    strikes = list(range(22500, 23500, 50))
    data = []
    for strike in strikes:
        call_iv = np.random.uniform(12, 18)
        put_iv = np.random.uniform(12, 18)
        delta_call = round(np.random.uniform(0.15, 0.25), 2)
        delta_put = round(np.random.uniform(-0.25, -0.15), 2)
        data.append({
            "strike": strike,
            "call_iv": round(call_iv, 2),
            "put_iv": round(put_iv, 2),
            "delta_call": delta_call,
            "delta_put": delta_put,
            "oi_call": np.random.randint(50000, 150000),
            "oi_put": np.random.randint(50000, 150000)
        })
    return pd.DataFrame(data), now.strftime("%H:%M:%S")

# App title
st.title("Nifty Iron Condor Option Seller Dashboard 🦉")
st.caption("Auto-refresh every 2 minutes | Built for ₹2 lakh capital")

# Fetch data
df, updated_time = fetch_option_data()
st.write(f"**Last updated:** {updated_time}")

# Filter based on delta criteria
condor_range = df[
    (df["delta_call"].between(0.15, 0.20)) &
    (df["delta_put"].between(-0.20, -0.15))
]

if not condor_range.empty:
    st.success("✅ Iron Condor Opportunity Found")
    best_strike = condor_range.iloc[len(condor_range)//2]
    st.write("### Suggested Setup (±0.15-0.20 delta):")
    st.code(f"""
Sell Call: {best_strike.strike + 50} CE (Δ ≈ {best_strike.delta_call})
Sell Put:  {best_strike.strike - 50} PE (Δ ≈ {best_strike.delta_put})
Buy Hedge Call: {best_strike.strike + 150} CE
Buy Hedge Put:  {best_strike.strike - 150} PE
    """)
else:
    st.warning("❌ No suitable strikes found in the 0.15–0.20 delta range.")

# Trade log section
st.markdown("---")
st.subheader("📘 Log Your Trades")

if "log" not in st.session_state:
    st.session_state["log"] = []

with st.form("trade_logger"):
    entry = st.text_input("Trade description")
    profit = st.number_input("Profit / Loss", value=0.0, format="%.2f")
    note = st.text_area("Note (optional)")
    submitted = st.form_submit_button("Add Trade")
    if submitted and entry:
        st.session_state["log"].append({
            "time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "entry": entry,
            "profit": profit,
            "note": note
        })

# Display log
if st.session_state["log"]:
    df_log = pd.DataFrame(st.session_state["log"])
    st.write("### Trade History")
    st.dataframe(df_log)
    total_pnl = df_log["profit"].sum()
    st.metric("Total P&L", f"₹ {total_pnl:.2f}")

# Footer
st.markdown("---")
st.caption("Made for Nifty weekly expiry | Auto-refresh every 2 mins | Built by ChatGPT + Streamlit")
