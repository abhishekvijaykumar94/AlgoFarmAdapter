from datetime import datetime

import pandas as pd
from algoLibs import CommonUtils, PropertyManager, AppConstants, RepositoryInfo, DataRepository
from algoLibs.dao.sql_alchemy_models import EquityFutureInstrument, EquityOptionInstrument, EquityCashInstrument
from algoLibs.dao.sql_alchemy_models.subscription_model import TickerSubscription
from algoLibs.data_objects.equity_cash_instruments_do import EquityCashInstrumentDO
from algoLibs.data_objects.equity_future_instruments_do import EquityFutureInstrumentDO
from algoLibs.data_objects.equity_option_instruments_do import EquityOptionInstrumentDO
from algoLibs.data_objects.ticker_subscription_do import TickerSubscriptionDO
from algoLibs.web_scraping.nse_web_scraper import NseWebScraper

from algoFarmAdapter.market_data import InstrumentDataFetcher
from algoFarmAdapter.market_data.expiry_calculator import ExpiryCalculator
from algoLibs.utils import Logger

log = Logger(__name__, log_file=True)
class TokenListGenerator:
    exchange_type = {"NSE": 1, "NFO": 2}

    def __init__(self, instrument_data_fetcher:InstrumentDataFetcher, expiry_calculator:ExpiryCalculator):
        self.instrument_data_fetcher = instrument_data_fetcher
        self.expiry_calculator = expiry_calculator
        self.data_repository = DataRepository()

    def stream_list(self, list_s, ex_type, instrument_type):
        tokens_df = pd.DataFrame()
        tokens_list = []
        token_df = self.instrument_data_fetcher.token_df
        indices = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']

        if len(list_s) > 0:
            if ex_type == "NSE":
                if any(s in list_s[0] for s in indices):
                    tokens_df = token_df[
                        (token_df['name'].isin(list_s)) &
                        (token_df['exch_seg'] == ex_type) &
                        (token_df['instrumenttype'] == instrument_type)
                    ]
                else:
                    tokens_df = token_df[
                        (token_df['name'].isin(list_s)) &
                        (token_df['exch_seg'] == ex_type) &
                        (token_df['symbol'].str.split('-').str[-1] == instrument_type)
                    ]
            elif ex_type == "NFO":
                if any(s in list_s[0] for s in indices):
                    tokens_df = token_df[
                        (token_df['symbol'].isin(list_s)) &
                        (token_df['exch_seg'] == ex_type) &
                        (token_df['instrumenttype'] == instrument_type)
                    ]
                else:
                    tokens_df = token_df[
                        (token_df['name'].isin(list_s)) &
                        (token_df['exch_seg'] == ex_type) &
                        (token_df['instrumenttype'] == instrument_type)
                    ]

            if not tokens_df.empty:
                tokens_df['date'] = datetime.today().strftime("%Y-%m-%d")
                tokens_list = [{"exchangeType": self.exchange_type[ex_type], "tokens": [token]} for token in tokens_df['token'].unique()]
            else:
                print(f"No tokens found for {list_s}")

        return tokens_df, tokens_list

    def fetch_fo_list(self):
        try:
            nse_fo_list_url = PropertyManager.getValue(AppConstants.NSE_FO_LIST_URL)
            nseWebScrapper = NseWebScraper(nse_fo_list_url)
            fo_list_html_table = nseWebScrapper.fetch_data()
            list_fo = nseWebScrapper.parse_data(fo_list_html_table)
        except (ValueError, TypeError):
            list_fo = pd.read_csv(CommonUtils.getFilePathFromDataDirectory('FO_list.csv'))
        finally:
            return list_fo

    def save_instruments(self,final_df:pd.DataFrame):

        for row,index in final_df.iterrows():
            if row.get('instrumenttype')=="FUTIDX":
                pass
            elif row.get('instrumenttype')=="OPTIDX":
                pass
            else:
                pass

    def save_equity_future_instruments(self,equity_cash, equity_futures):
        repository_info = RepositoryInfo(cache_domain=False)
        equity_future_instrument_list = []
        for index, row in equity_futures.iterrows():
            underlying_name = row.get('name')
            equity_cash_underlying_symbol = equity_cash[equity_cash['name'] == underlying_name]['symbol'].iloc[0]
            maturity_datetime = datetime.strptime(row.get('expiry'), "%d%b%Y")
            equity_future_instrument = EquityFutureInstrument(symbol=row.get('symbol'),
                                                              token=row.get('token'),
                                                              underlying_name=row.get('name'),
                                                              underlying_symbol=equity_cash_underlying_symbol,
                                                              instrument_type=row.get('instrumenttype'),
                                                              maturity=maturity_datetime,
                                                              lot_size=row.get('lotsize')
                                                              )
            try:
                equity_future_instrument_list.append(equity_future_instrument)
                equity_future_instrument_do = EquityFutureInstrumentDO(equity_future_instrument_list)
                self.data_repository.save(equity_future_instrument_do, repository_info)
            except Exception:
                log.info("Symbol:{}, already exists in the database".format(row.get('symbol')))

    def save_equity_option_instruments(self,equity_cash, equity_option):
        repository_info = RepositoryInfo(cache_domain=False)
        equity_option_instrument_list = []
        for index, row in equity_option.iterrows():
            underlying_name = row.get('name')
            equity_cash_underlying_symbol = equity_cash[equity_cash['name'] == underlying_name]['symbol'].iloc[0]
            maturity_datetime = datetime.strptime(row.get('expiry'), "%d%b%Y")
            equity_option_instrument = EquityOptionInstrument(symbol=row.get('symbol'),
                                                              token=row.get('token'),
                                                              underlying_name=row.get('name'),
                                                              underlying_symbol=equity_cash_underlying_symbol,
                                                              instrument_type=row.get('instrumenttype'),
                                                              maturity=maturity_datetime,
                                                              lot_size=row.get('lotsize'),
                                                              strike=row.get('strike')
                                                              )
            try:
                equity_option_instrument_list.append(equity_option_instrument)
                equity_option_instrument_do = EquityOptionInstrumentDO(equity_option_instrument_list)
                self.data_repository.save(equity_option_instrument_do, repository_info)
            except Exception:
                log.info("Symbol:{}, already exists in the database".format(row.get('symbol')))
    def save_equity_cash_instruments(self,equity_cash):
        repository_info = RepositoryInfo(cache_domain=False)
        equity_cash_instrument_list = []
        for index, row in equity_cash.iterrows():
            equity_cash_instrument = EquityCashInstrument(symbol=row.get('symbol'),
                                                          token=row.get('token'),
                                                          name=row.get('name'),
                                                          instrument_type=row.get('instrumenttype'),
                                                          exchange=row.get('exch_seg'))
            try:
                equity_cash_instrument_list.append(equity_cash_instrument)
                equity_cash_instrument_do = EquityCashInstrumentDO(equity_cash_instrument_list)
                self.data_repository.save(equity_cash_instrument_do, repository_info)
            except Exception:
                log.info("Symbol:{}, already exists in the database".format(row.get('symbol')))

    def save_subscription_symbols(self,subscribed_symbol_list):
        current_datetime = datetime.now()
        ticker_subscription_list = []
        repository_info = RepositoryInfo(cache_domain=False)
        for symbol in subscribed_symbol_list:
            ticker_subscription = TickerSubscription(ticker_symbol=symbol,
                                                     subscription_date=current_datetime)
            ticker_subscription_list.append(ticker_subscription)
        ticker_subscription_do = TickerSubscriptionDO(data=ticker_subscription_list)
        self.data_repository.save(ticker_subscription_do, repository_info)

    def generate_tokens(self):
        indices = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']
        list_fo=self.fetch_fo_list()
        list_fo.dropna(inplace=True)
        subscribed_symbol_list = []
        # Fetch the latest instrument data
        self.instrument_data_fetcher.fetch_instrument_data()

        # Get stock tokens
        stock_symbols = list_fo['Symbol'].to_list()[4:]
        stock_tokens_df, stock_tokens_list = self.stream_list(stock_symbols, "NSE", "EQ")

        # Get index tokens
        index_tokens_df, index_tokens_list = self.stream_list(indices, "NSE", "AMXIDX")

        equity_tokens_df = pd.concat([stock_tokens_df, index_tokens_df], ignore_index=True)
        subscribed_symbol_list.extend(equity_tokens_df['symbol'])
        self.save_equity_cash_instruments(equity_tokens_df)
        # Combine tokens
        token_list = stock_tokens_list + index_tokens_list

        # Generate option and future symbols
        option_syms = []
        future_syms = []
        for sym in indices:
            weekly_expiry_df = self.expiry_calculator.get_weekly_expiry(sym)
            option_syms.extend(weekly_expiry_df['symbol'])
            monthly_expiry_df = self.expiry_calculator.get_monthly_expiry(sym)
            future_syms.extend(monthly_expiry_df['symbol'].tolist())

        subscribed_symbol_list.extend(future_syms)
        subscribed_symbol_list.extend(option_syms)
        # Get option tokens
        options_df, options_tokens_list = self.stream_list(option_syms, "NFO", "OPTIDX")
        self.save_equity_option_instruments(equity_tokens_df,options_df)

        if options_tokens_list:
            token_list.extend(options_tokens_list)

        # Get future tokens
        futures_df, futures_tokens_list = self.stream_list(future_syms, "NFO", "FUTIDX")
        self.save_equity_future_instruments(equity_tokens_df, futures_df)

        if futures_tokens_list:
            token_list.extend(futures_tokens_list)

        # Combine all DataFrames for token mapping
        final_df = pd.concat([stock_tokens_df, index_tokens_df, options_df, futures_df], axis=0, ignore_index=True)

        self.save_subscription_symbols(subscribed_symbol_list)
        # Save the updated token mapping
        final_df.to_csv(CommonUtils.getFilePathFromDataDirectory('Token_mapping_test.csv'), index=False)

        return token_list
