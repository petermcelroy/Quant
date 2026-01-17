# config.py

# List of countries for the Domar Sustainability Audit
# Order: USA, Eurozone, Japan, China
COUNTRIES = ["USA", "Eurozone", "Japan", "China"]

# FRED Tickers for Real GDP and 10-Year Government Bond Yields
# Hardened for 2026 reporting cycles
COUNTRY_CONFIG = {
    "USA": {
        "GDP_Real": "GDPC1",        # Real Gross Domestic Product (US)
        "Rate_10Y": "DGS10"         # 10-Year Treasury Constant Maturity Rate
    },
    "Eurozone": {
        "GDP_Real": "NGDPRSAXDCEZQ", # Real GDP for Euro Area (19 countries)
        "Rate_10Y": "IRLTLT01EZM156N" # Euro Area 10-Year Government Bond Yield
    },
    "Japan": {
        "GDP_Real": "NGDPRSAXDCJPQ",  # Real GDP for Japan
        "Rate_10Y": "IRLTLT01JUM156N" # Japan 10-Year Government Bond Yield
    },
    "China": {
        "GDP_Real": "CHNGDPNQDSMEI",  # Real GDP for China (Quarterly)
        "Rate_10Y": "CHALTM01CNM661N" # China 10-Year Government Bond Yield
    }
}

# Start date for historical trend data
START_DATE = "2020-01-01"