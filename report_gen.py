import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
import os
from datetime import datetime
from dotenv import load_dotenv
import config

# Load Environment Variables
load_dotenv()
FRED_KEY = os.getenv('FRED_API_KEY')

def generate_professional_report():
    countries = config.COUNTRIES
    summary_data = []
    detail_html = ""

    # 1. HTML Header and Professional CSS Styling
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Domar Spread Sustainability Audit</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f0f2f5; color: #1c1e21; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; border-left: 6px solid #004a99; }}
            h1 {{ color: #004a99; margin-bottom: 10px; border-bottom: 2px solid #004a99; padding-bottom: 10px; }}
            .timestamp {{ color: #606770; font-size: 0.9em; margin-bottom: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background: white; }}
            th {{ background-color: #004a99; color: white; padding: 15px; text-align: left; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }}
            td {{ padding: 14px 15px; border-bottom: 1px solid #eef0f2; }}
            .status-red {{ background-color: #ffebe9; color: #cf222e; font-weight: bold; padding: 6px 10px; border-radius: 6px; border: 1px solid #ffcfcc; }}
            .status-green {{ background-color: #dafbe1; color: #1a7f37; font-weight: bold; padding: 6px 10px; border-radius: 6px; border: 1px solid #bcf0c7; }}
            .date-label {{ color: #6a737d; font-size: 11px; display: block; margin-top: 4px; font-style: italic; }}
            .country-name {{ font-weight: 700; color: #004a99; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <h1>Domar Sustainability Audit Dashboard</h1>
        <div class="timestamp"><strong>System Audit Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
    """

    # 2. Data Processing Loop
    for country in countries:
        cfg = config.COUNTRY_CONFIG[country]
        try:
            # Fetch raw data from FRED
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # Calculate Year-on-Year Real GDP Growth
            gdp_clean = df_raw['gdp'].dropna()
            g_growth = gdp_clean.pct_change(periods=4) * 100
            
            # Identify the most recent available data points (Asynchronous)
            latest_rate_idx = df_raw['rate'].last_valid_index()
            latest_gdp_idx = g_growth.last_valid_index()
            
            if latest_rate_idx is not None and latest_gdp_idx is not None:
                val_i = df_raw['rate'].loc[latest_rate_idx]
                val_g = g_growth.loc[latest_gdp_idx]
                domar_spread = val_i - val_g

                # Populate Summary Data
                summary_data.append({
                    'Country': country,
                    'i': val_i,
                    'i_date': latest_rate_idx.strftime('%Y-%m-%d'),
                    'g': val_g,
                    'g_date': latest_gdp_idx.strftime('%Y-%m-%d'),
                    'spread': domar_spread
                })

                # 3. Generate Historical Trend Chart
                # Use reindexing to align values for the historical line
                df_hist = pd.DataFrame(index=df_raw.index)
                df_hist['spread'] = df_raw['rate'].ffill() - g_growth.reindex(df_raw.index, method='ffill')
                df_hist = df_hist.dropna()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_hist.index, 
                    y=df_hist['spread'], 
                    name="Domar Spread", 
                    fill='tozeroy', 
                    line=dict(color='#004a99', width=2)
                ))
                fig.update_layout(
                    title=f"{country}: Historical Sustainability Trend (i - g)",
                    xaxis_title="Date",
                    yaxis_title="Spread %",
                    template="plotly_white",
                    height=350,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                detail_html += f"<div class='card'><h2>{country} Technical Detail</h2>"
                detail_html += fig.to_html(full_html=False, include_plotlyjs='cdn')
                detail_html += "</div>"

        except Exception as e:
            print(f"FAILED TO AUDIT {country}: {str(e)}")

    # 4. Build Live Summary Table
    table_html = """
    <div class='card'>
        <h2>Live Domar Status (Summary)</h2>
        <table>
            <thead>
                <tr>
                    <th>Country</th>
                    <th>10Y Yield (i)</th>
                    <th>Real GDP Growth (g)</th>
                    <th>Domar Spread (i - g)</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in summary_data:
        # LOGIC: Positive Spread = RED (Risk), Negative Spread = GREEN (Sustainable)
        color_class = "status-red" if item['spread'] > 0 else "status-green"
        
        table_html += f"""
            <tr>
                <td class="country-name">{item['Country']}</td>
                <td>{item['i']:.2f}%<span class="date-label">Obs: {item['i_date']}</span></td>
                <td>{item['g']:.2f}%<span class="date-label">Ref: {item['g_date']}</span></td>
                <td><span class="{color_class}">{item['spread']:.2f}%</span></td>
            </tr>
        """
    
    table_html += "</tbody></table></div>"

    # 5. Final File Assembly
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content + table_html + detail_html + "</body></html>")

if __name__ == "__main__":
    generate_professional_report()