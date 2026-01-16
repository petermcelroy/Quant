import os
import pandas as pd
import pandas_datareader.data as web
from dotenv import load_dotenv
import config

load_dotenv()
FRED_KEY = os.getenv('FRED_API_KEY')

def fetch_country_data(country_name):
    cfg = config.COUNTRY_CONFIG[country_name]
    
    try:
        # Fetch Real GDP and 10Y Rate
        df = web.DataReader([cfg["GDP_Real"], cfg['Rate_10Y']], 'fred', config.START_DATE, api_key=FRED_KEY)
        df.columns = ['gdp_raw', 'rate_raw']
        
        # 1. Isolate GDP releases to prevent daily 0% change errors
        gdp_series = df['gdp_raw'].dropna().drop_duplicates()
        
        # 2. Calculate YoY Growth: (Current Quarter / Quarter 1 Year Ago) - 1
        # This yields the ~2.3% figure for USA
        g_growth = gdp_series.pct_change(periods=4) * 100
        
        # 3. Create Daily DataFrame
        daily_df = pd.DataFrame(index=df.index)
        daily_df['rate'] = df['rate_raw'].ffill()
        daily_df['g_growth'] = g_growth.reindex(df.index, method='ffill')
        daily_df['domar_spread'] = daily_df['rate'] - daily_df['g_growth']
        daily_df['Country'] = country_name

        # 4. Filter for valid data only
        return daily_df.dropna(subset=['g_growth', 'rate']).query("g_growth != 0")

    except Exception as e:
        print(f"Error for {country_name}: {e}")
        return pd.DataFrame()

def main():
    master_list = []
    for country in config.COUNTRIES:
        print(f"Syncing {country} Real GDP Data...")
        df_c = fetch_country_data(country)
        if not df_c.empty:
            master_list.append(df_c)
            
    if master_list:
        if not os.path.exists('data'): os.makedirs('data')
        pd.concat(master_list).to_csv('data/historical_spreads.csv')
        print("\n[SUCCESS] CSV generated with Real GDP growth.")

if __name__ == "__main__":
    main()