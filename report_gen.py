import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import config

load_dotenv()
FRED_KEY = os.getenv('FRED_API_KEY')

def generate_professional_report():
    countries = config.COUNTRIES
    summary_data = []
    detail_html = ""

    # 1. Base HTML and CSS
    html_content = """
    <html>
    <head>
        <title>Domar Sustainability Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f4f7f9; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            th { background: #004a99; color: white; padding: 12px; text-align: left; }
            td { padding: 12px; border-bottom: 1px solid #eee; }
            .status-red { color: #cf222e; font-weight: bold; background: #ffebe9; padding: 4px; border-radius: 4px; }
            .status-green { color: #1a7f37; font-weight: bold; background: #dafbe1; padding: 4px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>Domar Sustainability Dashboard</h1>
        <p>Refreshed: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + """ UTC</p>
    """

    # 2. Data Processing Loop
    for country in countries:
        cfg = config.COUNTRY_CONFIG[country]
        try:
            # Fetch data with explicit error handling for FRED
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # Align Quarterly GDP to Daily Rates
            g_growth = df_raw['gdp'].dropna().pct_change(periods=4) * 100
            df = pd.DataFrame(index=df_raw.index)
            df['rate'] = df_raw['rate'].ffill()
            df['g_growth'] = g_growth.reindex(df_raw.index, method='ffill')
            df['obs_date'] = pd.Series(g_growth.index, index=g_growth.index).reindex(df_raw.index, method='ffill')
            df['spread'] = df['rate'] - df['g_growth']
            
            # Ensure we have at least one valid row
            df_clean = df.dropna()
            if not df_clean.empty:
                latest = df_clean.iloc[-1]
                summary_data.append({
                    'Country': country,
                    'Rate': f"{latest['rate']:.2f}%",
                    'Growth': f"{latest['g_growth']:.2f}%",
                    'Spread': latest['spread'],
                    'Source': latest['obs_date'].strftime('%Y-%m')
                })

                # Charting
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['spread'], name="Spread", fill='tozeroy'))
                fig.update_layout(title=f"{country} Historical Trend", height=300, template="plotly_white")
                detail_html += f"<div class='card'><h2>{country}</h2>" + fig.to_html(full_html=False, include_plotlyjs='cdn') + "</div>"
            else:
                print(f"No valid data calculated for {country}")

        except Exception as e:
            # If a country fails, we still want to know why
            summary_data.append({
                'Country': country,
                'Rate': 'ERR', 'Growth': 'ERR', 'Spread': 0, 'Source': str(e)[:20]
            })

    # 3. Build the Table (This section was likely being skipped)
    summary_table = "<div class='card'><h2>Live Domar Status</h2><table>"
    summary_table += "<tr><th>Country</th><th>10Y (i)</th><th>Real GDP (g)</th><th>Spread (i-g)</th><th>GDP Ref</th></tr>"
    
    for item in summary_data:
        # Precision Logic: Positive (i > g) is RED/Unstable. Negative (i < g) is GREEN/Sustainable.
        c_class = "status-red" if item['Spread'] > 0 else "status-green"
        summary_table += f"""
        <tr>
            <td><strong>{item['Country']}</strong></td>
            <td>{item['Rate']}</td>
            <td>{item['Growth']}</td>
            <td><span class='{c_class}'>{item['Spread']:.2f}%</span></td>
            <td>{item['Source']}</td>
        </tr>"""
    
    summary_table += "</table></div>"

    # 4. Final Write
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content + summary_table + detail_html + "</body></html>")

if __name__ == "__main__":
    generate_professional_report()
    