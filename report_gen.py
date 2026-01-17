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

    # 1. HTML/CSS Boilerplate (Professional Engineering Standard)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Domar Spread Sustainability Audit</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f0f2f5; color: #1c1e21; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; border-left: 6px solid #004a99; }}
            h1 {{ color: #004a99; border-bottom: 2px solid #004a99; padding-bottom: 10px; }}
            .timestamp {{ color: #606770; font-size: 0.9em; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; background: white; font-size: 14px; }}
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
        <div class="timestamp"><strong>Audit Execution (UTC):</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</div>
    """

    # 2. Data Retrieval and Audit Loop
    for country in countries:
        cfg = config.COUNTRY_CONFIG[country]
        try:
            # Fetch data with 2-year window to ensure growth calculation
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # Growth (g): YoY % Change of Real GDP
            gdp_clean = df_raw['gdp'].dropna()
            g_growth = gdp_clean.pct_change(periods=4) * 100
            
            # Rate (i): Latest valid 10Y Yield
            rate_clean = df_raw['rate'].dropna()
            
            if not rate_clean.empty and not g_growth.dropna().empty:
                # Get most recent values independently
                latest_i = rate_clean.iloc[-1]
                latest_i_date = rate_clean.index[-1]
                
                latest_g = g_growth.dropna().iloc[-1]
                latest_g_date = g_growth.dropna().index[-1]
                
                spread = latest_i - latest_g

                # Populate Summary
                summary_data.append({
                    'Country': country,
                    'i': round(latest_i, 3),
                    'i_date': latest_i_date.strftime('%Y-%m-%d'),
                    'g': round(latest_g, 3),
                    'g_date': latest_g_date.strftime('%Y-%m-%d'),
                    'Domar_Spread': round(spread, 3)
                })

                # 3. Create Trend Chart
                df_hist = pd.DataFrame(index=df_raw.index)
                df_hist['spread'] = df_raw['rate'].ffill() - g_growth.reindex(df_raw.index, method='ffill')
                df_hist = df_hist.dropna()

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['spread'], fill='tozeroy', line=dict(color='#004a99')))
                fig.update_layout(title=f"{country} Historical Spread (i - g)", template="plotly_white", height=300)
                detail_html += f"<div class='card'><h2>{country} Technical Analysis</h2>" + fig.to_html(full_html=False, include_plotlyjs='cdn') + "</div>"

        except Exception as e:
            print(f"AUDIT FAILURE FOR {country}: {e}")

    # 4. Summary Table Generation
    table_html = """
    <div class='card'>
        <h2>Live Domar Status Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Country</th>
                    <th>10Y Rate (i)</th>
                    <th>Real GDP Growth (g)</th>
                    <th>Domar Spread (i - g)</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in summary_data:
        # LOGIC: i - g > 0 is RED (Unsustainable Debt Trend)
        color_class = "status-red" if item['Domar_Spread'] > 0 else "status-green"
        
        table_html += f"""
            <tr>
                <td class="country-name">{item['Country']}</td>
                <td>{item['i']}%<span class="date-label">Obs: {item['i_date']}</span></td>
                <td>{item['g']}%<span class="date-label">Ref: {item['g_date']}</span></td>
                <td><span class="{color_class}">{item['Domar_Spread']}%</span></td>
            </tr>
        """
    
    table_html += "</tbody></table></div>"

    # 5. CSV and File Finalization
    if summary_data:
        pd.DataFrame(summary_data).to_csv("domar_audit.csv", index=False)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content + table_html + detail_html + "</body></html>")

if __name__ == "__main__":
    generate_professional_report()