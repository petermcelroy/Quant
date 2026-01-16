import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Quant Domar Strategy", layout="wide")
st.title("📈 Global Domar Spread Analysis")
st.markdown("### Real Sustainability Metrics: Spot $i$ vs. Real $g$")

# Force refresh button for data verification
if st.sidebar.button("Purge Cache & Reload"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_data():
    if not os.path.exists('data/historical_spreads.csv'):
        return pd.DataFrame()
    df = pd.read_csv('data/historical_spreads.csv', parse_dates=['DATE'])
    return df.sort_values(['Country', 'DATE'])

df = load_data()

if df.empty:
    st.error("Data file missing. Please run 'python data_loader.py' first.")
else:
    countries = df['Country'].unique()

    # --- SECTION 1: SPOT RATES ---
    st.subheader("10Y Benchmark Interest Rates ($i$)")
    cols_i = st.columns(len(countries))
    for idx, country in enumerate(countries):
        latest = df[df['Country'] == country].iloc[-1]
        cols_i[idx].metric(country, f"{latest['rate']:.2f}%")
        cols_i[idx].caption(f"Spot: {latest['DATE'].strftime('%Y-%m-%d')}")

    # --- SECTION 2: REAL GDP GROWTH ---
    st.subheader("Annual Real GDP Growth Rate ($g$)")
    cols_g = st.columns(len(countries))
    for idx, country in enumerate(countries):
        latest = df[df['Country'] == country].iloc[-1]
        # This should now show ~2.3% for USA
        cols_g[idx].metric(country, f"{latest['g_growth']:.2f}%")
        cols_g[idx].caption(f"Quarter: {latest['DATE'].year}-Q{latest['DATE'].quarter}")

    # --- SECTION 3: TECHNICAL TABLE ---
    st.divider()
    summary = []
    for country in countries:
        latest = df[df['Country'] == country].iloc[-1]
        summary.append({
            "Region": country,
            "10Y Rate": latest['rate'],
            "Real GDP Growth": latest['g_growth'],
            "Spread (i-g)": latest['domar_spread'],
            "As of": latest['DATE'].date()
        })
    
    st.table(pd.DataFrame(summary).style.format({
        "10Y Rate": "{:.2f}%", "Real GDP Growth": "{:.2f}%", "Spread (i-g)": "{:.2f}%"
    }))

    # --- SECTION 4: CHART ---
    st.divider()
    selected = st.sidebar.multiselect("Regions", options=countries, default=list(countries))
    filtered = df[df['Country'].isin(selected)]
    if not filtered.empty:
        fig = px.line(filtered, x='DATE', y='domar_spread', color='Country', title="Domar Spread Trend")
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)