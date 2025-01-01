# market_data_fetcher.py
import yfinance as yf
import pandas as pd

class MarketDataFetcher:
    def fetch_ltp(self, symbol):
        if symbol == "NIFTY":
            symbol = "^NSEI"
        elif symbol == "FINNIFTY":
            symbol = "NIFTY_FIN_SERVICE.NS"
        elif symbol == "BANKNIFTY":
            symbol = "^NSEBANK"
        else:
            symbol = symbol + ".NS"
        stock = yf.Ticker(symbol)
        current_price = stock.history(period='1d')
        return current_price
