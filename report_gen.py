import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
import config

# 1. Setup
load_dotenv()
FRED_KEY = os.getenv('FRED_API_KEY')

def generate_professional_report():
    """Fetches real GDP and Rates, calculates Domar Spread, and exports HTML."""
    all_figs = []
    
    # Create the Subplots: One row for each country
    countries = config.COUNTRIES
    fig = make_subplots(
        rows=len(countries), cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[f"{c} Sustainability Analysis" for c in countries]
    )

    for i, country in enumerate(countries):
        cfg = config.COUNTRY_CONFIG[country]
        try:
            print(f"Processing {country}...")
            # Fetch Data (Real GDP and 10Y Rate)
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # Calculate YoY Growth on unique GDP releases
            gdp_series = df_raw['gdp'].dropna().drop_duplicates()
            g_growth = gdp_series.pct_change(periods=4) * 100
            
            # Align and calculate spread
            df = pd.DataFrame(index=df_raw.index)
            df['rate'] = df_raw['rate'].ffill()
            df['g_growth'] = g_growth.reindex(df_raw.index, method='ffill')
            df['spread'] = df['rate'] - df['g_growth']
            df = df.dropna()

            # Add traces to subplot
            row = i + 1
            # Rate and Growth
            fig.add_trace(go.Scatter(x=df.index, y=df['rate'], name=f"{country} Rate (i)", line=dict(width=2)), row=row, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['g_growth'], name=f"{country} Real Growth (g)", line=dict(dash='dash')), row=row, col=1)
            # Spread
            fig.add_trace(go.Scatter(x=df.index, y=df['spread'], name=f"{country} Spread (i-g)", fill='tozeroy', opacity=0.3), row=row, col=1)
            
            # Add horizontal zero line for sustainability threshold
            fig.add_hline(y=0, line_dash="solid", line_color="black", row=row, col=1)

        except Exception as e:
            print(f"Skipping {country} due to error: {e}")

    # 2. Formatting the final document
    fig.update_layout(
        height=400 * len(countries), 
        title_text="Global Domar Spread & Sustainability Report (Real GDP Basis)",
        template="plotly_white",
        showlegend=True,
        margin=dict(t=100, b=50)
    )
    
    # 3. Save to Standalone HTML
    output_path = "Domar_Sustainability_Report.html"
    fig.write_html(output_path, include_plotlyjs=True)
    print(f"\n✅ SUCCESS: Report created at {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_professional_report()
    