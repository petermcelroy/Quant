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
    countries = config.COUNTRIES
    summary_data = []
    detail_html = ""

    # CSS for Professional Engineering Reporting
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Domar Spread Sustainability Audit</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f0f2f5; color: #1c1e21; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; }}
            h1 {{ color: #004a99; border-bottom: 2px solid #004a99; padding-bottom: 10px; }}
            .timestamp {{ color: #606770; font-size: 0.9em; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; background: white; font-size: 14px; }}
            th {{ background-color: #004a99; color: white; padding: 15px; text-align: left; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }}
            td {{ padding: 14px 15px; border-bottom: 1px solid #eef0f2; }}
            .status-red {{ background-color: #ffebe9; color: #cf222e; font-weight: bold; padding: 6px 10px; border-radius: 6px; border: 1px solid #ffcfcc; }}
            .status-green {{ background-color: #dafbe1; color: #1a7f37; font-weight: bold; padding: 6px 10px; border-radius: 6px; border: 1px solid #bcf0c7; }}
            .date-label {{ color: #6a737d; font-size: 11px; display: block; margin-top: 4px; font-style: italic; }}
            .country-name {{ font-weight: 700; color: #004a99; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <h1>Domar Sustainability Audit Dashboard</h1>
        <div class="timestamp"><strong>Audit Execution:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
    """

    for country in countries:
        try:
            cfg = config.COUNTRY_CONFIG[country]
            # Fetch data using API Key
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # Growth Calculation
            gdp_clean = df_raw['gdp'].dropna()
            g_growth = gdp_clean.pct_change(periods=4) * 100
            
            # Independent Metric Extraction (Prevents China/Japan from disappearing)
            rate_series = df_raw['rate'].dropna()
            growth_series = g_growth.dropna()

            if not rate_series.empty and not growth_series.empty:
                val_i = rate_series.iloc[-1]
                date_i = rate_series.index[-1].strftime('%Y-%m-%d')
                
                val_g = growth_series.iloc[-1]
                date_g = growth_series.index[-1].strftime('%Y-%m-%d')
                
                spread = val_i - val_g

                summary_data.append({
                    'Country': country,
                    'i': round(val_i, 3),
                    'i_date': date_i,
                    'g': round(val_g, 3),
                    'g_date': date_g,
                    'Domar_Spread': round(spread, 3)
                })

                # Create Plotly Chart
                df_h = pd.DataFrame(index=df_raw.index)
                df_h['spread'] = df_raw['rate'].ffill() - g_growth.reindex(df_raw.index, method='ffill')
                fig = go.Figure(go.Scatter(x=df_h.index, y=df_h['spread'], fill='tozeroy', line=dict(color='#004a99')))
                fig.update_layout(title=f"{country} Historical Spread", template="plotly_white", height=300)
                detail_html += f"<div class='card'><h2>{country}</h2>" + fig.to_html(full_html=False, include_plotlyjs='cdn') + "</div>"

        except Exception as e:
            print(f"FAILED {country}: {e}")

    # Build Table
    table_html = "<div class='card'><table><thead><tr><th>Country</th><th>10Y Rate (i)</th><th>Real GDP (g)</th><th>Spread (i-g)</th></tr></thead><tbody>"
    for item in summary_data:
        color = "status-red" if item['Domar_Spread'] > 0 else "status-green"
        table_html += f"""
            <tr>
                <td class="country-name">{item['Country']}</td>
                <td>{item['i']}%<span class="date-label">Obs: {item['i_date']}</span></td>
                <td>{item['g']}%<span class="date-label">Ref: {item['g_date']}</span></td>
                <td><span class="{color}">{item['Domar_Spread']}%</span></td>
            </tr>"""
    table_html += "</tbody></table></div>"

    # Export Files
    if summary_data:
        pd.DataFrame(summary_data).to_csv("domar_audit.csv", index=False)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content + table_html + detail_html + "</body></html>")

if __name__ == "__main__":
    generate_professional_report()