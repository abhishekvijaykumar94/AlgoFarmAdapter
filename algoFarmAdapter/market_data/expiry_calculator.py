# expiry_calculator.py
import pandas as pd
from datetime import datetime

from algoFarmAdapter.market_data import InstrumentDataFetcher, MarketDataFetcher


class ExpiryCalculator:
    limit_tick = {"NIFTY": 0.02, "BANKNIFTY": 0.03, "FINNIFTY": 0.02}

    def __init__(self, instrument_data_fetcher:InstrumentDataFetcher, market_data_fetcher:MarketDataFetcher):
        self.instrument_data_fetcher = instrument_data_fetcher
        self.market_data_fetcher = market_data_fetcher

    def get_monthly_expiry(self, sym, type='current'):
        if type == 'historical':
            df = self.instrument_data_fetcher.fetch_historical_instrument_data()
        else:
            df = self.instrument_data_fetcher.fetch_instrument_data()

        fut_sym = df[(df.exch_seg == 'NFO') & (df.instrumenttype == 'FUTIDX') & (df.name == sym)]
        fut_sym['dummy_expiry'] = pd.to_datetime(fut_sym["expiry"], format='%d%b%Y', errors='coerce')
        fut_sym = fut_sym[fut_sym['dummy_expiry'] >= datetime.today()]
        fut_sym.sort_values('dummy_expiry', inplace=True)
        return fut_sym.iloc[:2]

    def get_weekly_expiry(self, sym, type='current'):
        if type == 'historical':
            df = self.instrument_data_fetcher.fetch_historical_instrument_data()
        else:
            df = self.instrument_data_fetcher.fetch_instrument_data()

        fut_sym = df[(df.exch_seg == 'NFO') & (df.name == sym)]
        fut_sym['dummy_expiry'] = pd.to_datetime(fut_sym["expiry"], format='%d%b%Y', errors='coerce')
        fut_sym.sort_values('dummy_expiry', inplace=True)

        fut_sym_price = self.market_data_fetcher.fetch_ltp(sym)
        if len(fut_sym_price) == 0:
            token = df[(df['name'] == sym) & (df['exch_seg'] == "NSE") &
                       (df['instrumenttype'] == "AMXIDX")]['token']
            fut_sym_price = self.market_data_fetcher.fetch_ltp(sym)

        if len(fut_sym_price) > 0:
            ltp = fut_sym_price['Close'].iloc[-1]
            expiries = fut_sym.dummy_expiry.unique()
            expiries = [x for x in expiries if pd.to_datetime(str(x)).strftime("%Y-%m-%d") >=
                        datetime.today().strftime('%Y-%m-%d')][:2]

            fut_sym['strike'] = fut_sym['strike'].astype('float') / 100
            fut_sym = fut_sym[(fut_sym['dummy_expiry'].isin(expiries)) &
                              (abs(fut_sym['strike'] / ltp - 1) <= self.limit_tick[sym])]

            return fut_sym
        else:
            return pd.DataFrame(columns=['symbol'])
