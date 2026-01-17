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

    # Header and Styling
    html_content = """
    <html>
    <head>
        <title>Domar Sustainability Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; background: #f0f2f5; color: #1c1e21; }
            .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; }
            h1 { color: #004a99; border-bottom: 2px solid #004a99; padding-bottom: 10px; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; background: white; border-radius: 8px; overflow: hidden; }
            th { background-color: #004a99; color: white; padding: 15px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 12px; }
            td { padding: 14px 15px; border-bottom: 1px solid #eef0f2; font-size: 14px; }
            .status-red { background-color: #ffebe9; color: #cf222e; font-weight: bold; padding: 4px 8px; border-radius: 4px; }
            .status-green { background-color: #dafbe1; color: #1a7f37; font-weight: bold; padding: 4px 8px; border-radius: 4px; }
            .obs-date { color: #6a737d; font-size: 11px; }
        </style>
    </head>
    <body>
        <h1>Domar Sustainability Dashboard</h1>
        <p><strong>Refreshed:</strong> """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + """ UTC</p>
    """

    for country in countries:
        cfg = config.COUNTRY_CONFIG[country]
        try:
            # 1. Data Fetching
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # 2. Calculation
            g_growth = df_raw['gdp'].dropna().pct_change(periods=4) * 100
            df = pd.DataFrame(index=df_raw.index)
            df['rate'] = df_raw['rate'].ffill()
            df['g_growth'] = g_growth.reindex(df_raw.index, method='ffill')
            df['gdp_obs_date'] = pd.Series(df_raw['gdp'].dropna().index).reindex(df_raw.index, method='ffill')
            df['spread'] = df['rate'] - df['g_growth']
            df = df.dropna()

            # 3. Store Latest for Summary
            latest = df.iloc[-1]
            summary_data.append({
                'Country': country,
                'Rate': f"{latest['rate']:.2f}%",
                'Growth': f"{latest['g_growth']:.2f}%",
                'Spread': latest['spread'],
                'Source': latest['gdp_obs_date'].strftime('%Y-%m')
            })

            # 4. Generate Country Detail (Charts)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['spread'], name="Domar Spread", fill='tozeroy', line=dict(color='#004a99')))
            fig.update_layout(title=f"{country} Historical Spread Trend", height=350, template="plotly_white", margin=dict(l=0,r=0,t=40,b=0))
            detail_html += f"<div class='card'><h2>{country} Detail</h2>" + fig.to_html(full_html=False, include_plotlyjs='cdn') + "</div>"

        except Exception as e:
            print(f"Error {country}: {e}")

    # Build Summary Table (Live Domar at the Top)
    summary_html = "<div class='card'><h2>Live Domar Status (All Countries)</h2><table>"
    summary_html += "<tr><th>Country</th><th>10Y Yield (i)</th><th>Real GDP Growth (g)</th><th>Domar Spread (i-g)</th><th>GDP Data Ref</th></tr>"
    
    for item in summary_data:
        # LOGIC: Positive = Red (Bad), Negative = Green (Good)
        color_class = "status-red" if item['Spread'] > 0 else "status-green"
        summary_html += f"""
            <tr>
                <td><strong>{item['Country']}</strong></td>
                <td>{item['Rate']}</td>
                <td>{item['Growth']}</td>
                <td><span class='{color_class}'>{item['Spread']:.2f}%</span></td>
                <td class='obs-date'>{item['Source']}</td>
            </tr>"""
    summary_html += "</table></div>"

    # Assemble Final HTML
    final_output = html_content + summary_html + detail_html + "</body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_output)

if __name__ == "__main__":
    generate_professional_report()