import config
from data_loader import fetch_country_data
import pandas as pd
import os

def main():
    if not os.path.exists('data'):
        os.makedirs('data')

    master_list = []

    for country in config.COUNTRIES:
        try:
            print(f"Extracting {country}...")
            df = fetch_country_data(country)
            df['Country'] = country  # Labeling before merge
            master_list.append(df)
        except Exception as e:
            print(f"Failed to process {country}: {e}")

    if master_list:
        full_df = pd.concat(master_list)
        full_df.to_csv('data/historical_spreads.csv')
        print(f"\nSaved {len(master_list)} countries to data/historical_spreads.csv")
    else:
        print("\nNo data collected. Check API keys and tickers.")

if __name__ == "__main__":
    main()