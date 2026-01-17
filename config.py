# config.py
COUNTRIES = ["USA", "Eurozone", "Japan", "China"]

COUNTRY_CONFIG = {
    "USA": {
        "GDP_Real": "GDPC1",        # Real GDP (Billions of Chained 2017 Dollars)
        "Rate_10Y": "DGS10"         # 10-Year Treasury Yield
    },
    "Eurozone": {
        "GDP_Real": "NGDPRSAXDCEZQ", # Real GDP for Euro Area
        "Rate_10Y": "IRLTLT01EZM156N" # 10-Year Gov Bond Yield (Benchmark)
    },
    "Japan": {
        "GDP_Real": "NGDPRSAXDCJPQ",  # Real GDP for Japan
        "Rate_10Y": "IRLTLT01JUM156N" # 10-Year Gov Bond Yield for Japan
    },
    "China": {
        "GDP_Real": "CHNGDPNQDSMEI",  # Real GDP for China
        "Rate_10Y": "CHALTM01CNM661N" # 10-Year Gov Bond Yield for China
    }
}

START_DATE = "2020-01-01"