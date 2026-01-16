# config.py
START_DATE = '2015-01-01'

COUNTRIES = ["USA", "UK", "Eurozone", "Japan", "Australia"]

COUNTRY_CONFIG = {
    "USA": {
        "GDP_Real": "GDPC1", 
        "Rate_10Y": "DGS10",
    },
    "UK": {
        "GDP_Real": "NGDPRSAXDCGBQ", 
        "Rate_10Y": "IRLTLT01GBM156N",
    },
    "Eurozone": {
        "GDP_Real": "CLV10MEURB1GQSCAEA20Q", 
        "Rate_10Y": "IRLTLT01EZM156N",
    },
    "Japan": {
        "GDP_Real": "JPNRGDPEXP", 
        "Rate_10Y": "IRLTLT01JPM156N",
    },
    "Australia": {
        "GDP_Real": "NAEXKP01AUQ661S", 
        "Rate_10Y": "IRLTLT01AUM156N",
    }
}