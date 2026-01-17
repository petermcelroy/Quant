import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import config

load_dotenv()
FRED_KEY = os.getenv('FRED_API_KEY')

def generate_audit_report():
    countries = config.COUNTRIES
    html_content = """
    <html>
    <head>
        <title>Domar Spread Engineering Audit</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f8f9fa; }
            .container { background: white; padding: 25px; border-radius: 4px; border-left: 5px solid #004a99; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 50px; }
            table { border-collapse: collapse; width: 100%; margin-top: 15px; font-size: 13px; }
            th { background-color: #004a99; color: white; padding: 12px; text-align: left; border: 1px solid #ddd; }
            td { padding: 10px; border: 1px solid #ddd; text-align: left; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .status-red { color: #d9534f; font-weight: bold; }
            .status-green { color: #5cb85c; font-weight: bold; }
            .obs-date { color: #666; font-style: italic; font-size: 11px; }
        </style>
    </head>
    <body>
        <h1>Domar Spread Analysis: Professional Audit Report</h1>
        <p><strong>Report Execution Time:</strong> """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + """ (UTC)</p>
        <hr>
    """

    for country in countries:
        cfg = config.COUNTRY_CONFIG[country]
        try:
            # 1. Precise Data Retrieval
            df_raw = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
            df_raw.columns = ['gdp', 'rate']
            
            # 2. Calculation & Timestamp Mapping
            gdp_raw = df_raw['gdp'].dropna()
            g_growth = gdp_raw.pct_change(periods=4) * 100
            
            # Create a mapping of when the GDP was actually observed
            obs_dates = pd.Series(gdp_raw.index, index=gdp_raw.index)

            df = pd.DataFrame(index=df_raw.index)
            df['rate'] = df_raw['rate'].ffill()
            df['g_growth'] = g_growth.reindex(df_raw.index, method='ffill')
            df['gdp_obs_date'] = obs_dates.reindex(df_raw.index, method='ffill')
            df['spread'] = df['rate'] - df['g_growth']
            
            # We show the last 15 business days to verify the daily 'forward-fill'
            df_audit = df.dropna().tail(15)

            # 3. HTML Table Construction
            table_html = f"""
            <div class='container'>
                <h2>{country} Sustainability Audit</h2>
                <table>
                    <tr>
                        <th>Calculation Date</th>
                        <th>10Y Rate (i)</th>
                        <th>Real GDP Growth (g)</th>
                        <th>Domar Spread (i-g)</th>
                        <th>GDP Source Date</th>
                    </tr>"""
            
            for date, row in df_audit.iterrows():
                spread_style = "status-red" if row['spread'] > 0 else "status-green"
                obs_date_str = row['gdp_obs_date'].strftime('%Y-%m-%d')
                
                table_html += f"""
                    <tr>
                        <td>{date.strftime('%Y-%m-%d')}</td>
                        <td>{row['rate']:.2f}%</td>
                        <td>{row['g_growth']:.2f}%</td>
                        <td class='{spread_style}'>{row['spread']:.2f}%</td>
                        <td class='obs-date'>Ref: {obs_date_str}</td>
                    </tr>"""
            table_html += "</table>"

            # 4. Charting
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['rate'], name="10Y Bond Yield (i)", line=dict(color='#004a99')))
            fig.add_trace(go.Scatter(x=df.index, y=df['g_growth'], name="GDP Growth (g)", line=dict(color='#f0ad4e', dash='dash')))
            fig.add_trace(go.Scatter(x=df.index, y=df['spread'], name="Domar Spread", fill='tozeroy', fillcolor='rgba(217, 83, 79, 0.1)', line=dict(color='#d9534f')))
            
            fig.update_layout(
                title=f"{country}: Sustainability Trend (i vs g)",
                xaxis_title="Timeline",
                yaxis_title="Percentage (%)",
                template="plotly_white",
                height=450,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
            html_content += table_html + chart_html + "</div>"

        except Exception as e:
            html_content += f"<div class='container' style='border-left-color:red;'><strong>Fault Detected in {country}:</strong> {str(e)}</div>"

    html_content += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_audit_report()