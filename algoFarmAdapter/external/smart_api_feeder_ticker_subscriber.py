# import pandas as pd
# from algoLibs import CommonUtils
#
#
# class SmartApiFeederTickerSubscriber:
#
#     def __init__(self):
#         token_file_path = CommonUtils.getFilePathFromDataDirectory('Token_mapping.csv')
#         self.hist_token_df = pd.read_csv(token_file_path)
#         self.hist_token_df['token'] = self.hist_token_df['token'].astype('str')
#         self.indices = ['NIFTY','BANKNIFTY','FINNIFTY']
#
#     def get_tokens_to_subscribe(self):
#         stock_tokens_df, token_list = stream_list(listFO['Symbol'].to_list()[4:], "NSE", "EQ")
#         index_token_df, indices_token = stream_list(indices, "NSE", "AMXIDX")
#         token_list.extend(indices_token)
#
#         option_syms = []
#         future_syms = []
#         for sym in indices:
#             # option_syms.extend(fetch_fut_option_symbol_info(sym,"OPT"))
#             option_syms.extend(get_weekly_expiry(sym)['symbol'])
#             future_syms.extend(get_monthly_expiry(sym)['symbol'].to_list())
#
#         index_options_df, options_tokens = stream_list(option_syms, "NFO", "OPTIDX")
#         if (options_tokens):
#             token_list.extend(options_tokens)
#         index_future_df, fut_tokens = stream_list(future_syms, "NFO", "FUTIDX")
#         if (fut_tokens):
#             token_list.extend(fut_tokens)
#         Final = pd.concat([stock_tokens_df, index_token_df, index_options_df, index_future_df], axis=0,
#                           ignore_index=True)
#         Final.to_csv(CommonUtils.getFilePathFromDataDirectory('Token_mapping.csv'), index=False)
#
#         return token_list
#
#     def get_weekly_expiry(self,sym, type='current'):
#         if (type == 'historical'):
#             df = hist_token_df
#             fut_sym = df[(df.exch_seg == 'NFO') & (df.name == sym)]
#             fut_sym['dummy_expiry'] = pd.to_datetime(fut_sym["expiry"], format='%d%b%y')
#             fut_sym.sort_values('dummy_expiry', inplace=True)
#             return fut_sym['expiry'].unique()
#
#         else:
#             response = req.urlopen(instrument_url)
#             instrument_list = json.loads(response.read())
#             df = pd.DataFrame.from_dict(instrument_list)
#             fut_sym = df[(df.exch_seg == 'NFO') & (df.name == sym)]
#             fut_sym['dummy_expiry'] = pd.to_datetime(fut_sym["expiry"], format='%d%b%Y')
#             fut_sym.sort_values('dummy_expiry', inplace=True)
#             fut_sym_price = fetchLTP(sym)
#             if (len(fut_sym_price) == 0):
#                 token = df[(df['name'] == sym) & (df['exch_seg'] == "NSE") & (df['instrumenttype'] == "AMXIDX")][
#                     'token']
#                 fut_sym_price = fetchLTP(sym)
#
#             if (len(fut_sym_price) > 0):
#                 # fut_sym_price.sort_values('_time', inplace=True, ascending=False)
#                 ltp = fut_sym_price['Close'].iloc[-1]
#                 expiries = fut_sym.dummy_expiry.unique()
#                 expiries = [x for x in expiries if
#                             pd.to_datetime(str(x)).strftime("%Y-%m-%d") >= datetime.today().strftime('%Y-%m-%d')][:2]
#
#                 fut_sym['strike'] = fut_sym['strike'].astype('float') / 100
#                 fut_sym = fut_sym[
#                     (fut_sym['dummy_expiry'].isin(expiries)) & (abs(fut_sym['strike'] / ltp - 1) <= limit_tick[sym])]
#
#                 return fut_sym
#             else:
#                 return pd.DataFrame(columns=['symbol'])
#
#     def get_monthly_expiry(self,sym, type='current'):
#         if (type == 'historical'):
#             df = hist_token_df
#             fut_sym = df[(df.exch_seg == 'NFO') & (df.instrumenttype == 'FUTIDX') & (df.name == sym)]
#             fut_sym['dummy_expiry'] = pd.to_datetime(fut_sym["expiry"], format='%d%b%y')
#             fut_sym.sort_values('dummy_expiry', inplace=True)
#             return fut_sym
#         else:
#             response = req.urlopen(instrument_url)
#             instrument_list = json.loads(response.read())
#             df = pd.DataFrame.from_dict(instrument_list)
#             fut_sym = df[(df.exch_seg == 'NFO') & (df.instrumenttype == 'FUTIDX') & (df.name == sym)]
#             fut_sym['dummy_expiry'] = pd.to_datetime(fut_sym["expiry"], format='%d%b%Y')
#             fut_sym = fut_sym[fut_sym['dummy_expiry'] >= datetime.today()]
#             fut_sym.sort_values('dummy_expiry', inplace=True)
#
#             return fut_sym.iloc[:2]
#
#     def stream_list(self,list_s, ex_type, instrument_type, token_info="list", strat_test=0):
#         tokens = []
#         token_df = globals()['token_df']
#
#         if (len(list_s) > 0):
#             if ex_type == "NSE":
#                 if (len([s for s in indices if s in list_s[0]])):
#                     tokens = token_df[(token_df['name'].isin(list_s)) & (token_df['exch_seg'] == ex_type) & (
#                                 token_df['instrumenttype'] == instrument_type)]
#                 else:
#                     tokens = token_df[(token_df['name'].isin(list_s)) & (token_df['exch_seg'] == ex_type) & (
#                                 token_df["symbol"].str.split('-').str[-1] == instrument_type)]
#             elif ex_type == "NFO":
#
#                 if (len([s for s in indices if s in list_s[0]])):
#                     tokens = token_df[(token_df['symbol'].isin(list_s)) & (token_df['exch_seg'] == ex_type) & (
#                                 token_df['instrumenttype'] == instrument_type)]
#                 else:
#                     tokens = token_df[(token_df['name'].isin(list_s)) & (token_df['exch_seg'] == ex_type) & (
#                             token_df['instrumenttype'] == instrument_type)]
#
#             if (len(tokens) > 0):
#                 if (token_info == "list"):
#                     ## Returning for smart api
#                     tokens['date'] = datetime.today().strftime("%Y-%m-%d")
#                     return tokens, [{"exchangeType": exchange_type[ex_type], "tokens": [token]} for token in
#                                     set(tokens['token'])]
#                 else:
#                     return tokens['token'].iloc[0]
#             else:
#                 print("No token found")
#                 return []
