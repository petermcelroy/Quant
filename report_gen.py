import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
import os
from datetime import datetime
from dotenv import load_dotenv
import config

load_dotenv()
FRED_KEY = os.getenv('FRED_API_KEY')

def generate_professional_report():
    summary_data = []
    detail_html = ""

    html_start = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Domar Audit</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f0f2f5; color: #1c1e21; }}
        .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; border-top: 5px solid #004a99; }}
        h1 {{ color: #004a99; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; background: white; }}
        th {{ background-color: #004a99; color: white; padding: 12px; text-align: left; text-transform: uppercase; font-size: 11px; }}
        td {{ padding: 12px; border-bottom: 1px solid #eef0f2; }}
        .status-red {{ background-color: #ffebe9; color: #cf222e; font-weight: bold; padding: 5px 10px; border-radius: 6px; }}
        .status-green {{ background-color: #dafbe1; color: #1a7f37; font-weight: bold; padding: 5px 10px; border-radius: 6px; }}
        .date-label {{ color: #6a737d; font-size: 11px; display: block; }}
    </style></head><body><h1>Domar Sustainability Audit Dashboard</h1>
    <p><strong>Refreshed:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>"""

    for country in config.COUNTRIES:
        print(f"--- AUDIT START: {country} ---")
        try:
            cfg = config.COUNTRY_CONFIG[country]
            # Fetch data with API Key
            df = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df.columns = ['gdp', 'rate']
            
            g_growth = df['gdp'].dropna().pct_change(periods=4) * 100
            r_latest, g_latest = df['rate'].dropna(), g_growth.dropna()

            if not r_latest.empty and not g_latest.empty:
                i_val, i_date = r_latest.iloc[-1], r_latest.index[-1].strftime('%Y-%m-%d')
                g_val, g_date = g_latest.iloc[-1], g_latest.index[-1].strftime('%Y-%m-%d')
                spread = i_val - g_val

                summary_data.append({
                    'Country': country, 'i': i_val, 'i_date': i_date,
                    'g': g_val, 'g_date': g_date, 'Spread': spread
                })

                df_h = pd.DataFrame(index=df.index)
                df_h['s'] = df['rate'].ffill() - g_growth.reindex(df.index, method='ffill')
                fig = go.Figure(go.Scatter(x=df_h.index, y=df_h['s'], fill='tozeroy', line=dict(color='#004a99')))
                fig.update_layout(title=f"{country} Historical Spread", template="plotly_white", height=300)
                detail_html += f"<div class='card'><h2>{country}</h2>{fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>"
                print(f"SUCCESS: {country} data captured.")
            else:
                print(f"WARNING: {country} returned empty dataframes.")

        except Exception as e:
            print(f"ERROR: Failed to process {country}. Detailed error: {e}")
            # Continue to the next country instead of crashing
            continue 

    # Building the Table
    table_html = "<div class='card'><h2>Live Status</h2><table><tr><th>Country</th><th>Rate (i)</th><th>Growth (g)</th><th>Spread (i-g)</th></tr>"
    for row in summary_data:
        color = "status-red" if row['Spread'] > 0 else "status-green"
        table_html += f"""<tr><td><b>{row['Country']}</b></td>
            <td>{row['i']:.2f}%<span class='date-label'>{row['i_date']}</span></td>
            <td>{row['g']:.2f}%<span class='date-label'>{row['g_date']}</span></td>
            <td><span class='{color}'>{row['Spread']:.2f}%</span></td></tr>"""
    
    if summary_data:
        pd.DataFrame(summary_data).to_csv("domar_audit.csv", index=False)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_start + table_html + "</table></div>" + detail_html + "</body></html>")
        print(f"--- AUDIT COMPLETE: {len(summary_data)} countries saved ---")

if __name__ == "__main__":
    generate_professional_report()