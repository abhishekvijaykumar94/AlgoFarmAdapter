from typing import List

import numpy as np
import pandas as pd
from algoLibs import TickMarketFeedColumns, AppConstants
from algoLibs.converters.equity_market_data_converter import EquityMarketDataConverter

class SmartApiInputFields():
    best_5_buy_data = "best_5_buy_data"
    best_5_sell_data = "best_5_sell_data"
    exchange_timestamp = "exchange_timestamp"
    quantity = "quantity"
    price = "price"
    """
    Sample format for input Smart Api JSON Message
        "subscription_mode": 3,
        "exchange_type": 2,
        "token": "48840",
        "sequence_number": 11586881,
        "exchange_timestamp": 1718081943000,
        "last_traded_price": 13895,
        "subscription_mode_val": "SNAP_QUOTE",
        "last_traded_quantity": 160,
        "average_traded_price": 17484,
        "volume_trade_for_the_day": 37920,
        "total_buy_quantity": 5840.0,
        "total_sell_quantity": 7800.0,
        "open_price_of_the_day": 26085,
        "high_price_of_the_day": 26085,
        "low_price_of_the_day": 13690,
        "closed_price": 26085,
        "last_traded_timestamp": 1718081943,
        "open_interest": 7680,
        "open_interest_change_percentage": -4605063077798901881,
        "upper_circuit_limit": 53940,
        "lower_circuit_limit": 5,
        "52_week_high_price": 97780,
        "52_week_low_price": 0,
        "best_5_buy_data": [
            {"flag": 0, "quantity": 80, "price": 14135, "no of orders": 1},
            {"flag": 0, "quantity": 40, "price": 14160, "no of orders": 1},
            {"flag": 0, "quantity": 40, "price": 14210, "no of orders": 1},
            {"flag": 0, "quantity": 480, "price": 14215, "no of orders": 1},
            {"flag": 0, "quantity": 240, "price": 14240, "no of orders": 1},
        ],
        "best_5_sell_data": [
            {"flag": 1, "quantity": 760, "price": 13865, "no of orders": 2},
            {"flag": 1, "quantity": 600, "price": 13860, "no of orders": 1},
            {"flag": 1, "quantity": 80, "price": 13840, "no of orders": 1},
            {"flag": 1, "quantity": 240, "price": 13800, "no of orders": 1},
            {"flag": 1, "quantity": 400, "price": 13795, "no of orders": 1},
    """

class SmartApiEquityMarketDataConverter(EquityMarketDataConverter):
    """
    Converts Input market data from Angel Broking's Smart API to native Algo Farm Format
    """
#
#     def convert_to_native_format(self,batch_data:pd.DataFrame)->pd.DataFrame:
#         if batch_data is None or batch_data.empty:
#             return []
#
#             # df[TickMarketFeedColumns.time] = pd.to_datetime(df[SmartApiInputFields.exchange_timestamp] // 1000,
#             #                                                    unit='s', utc=True)
#         batch_data[TickMarketFeedColumns.time] = batch_data[SmartApiInputFields.exchange_timestamp]
#         batch_data['measurement'] = AppConstants.Equity_Market_Data_Table
#
#         symbol_column = [TickMarketFeedColumns.tag]
#         symbol_df = batch_data[symbol_column]
#         batch_data['tags'] = symbol_df.to_dict('records')
#
#         buy_quantity = [entry[0][SmartApiInputFields.quantity] if entry else None for entry in
#                         batch_data[SmartApiInputFields.best_5_buy_data]]
#         buy_price = [entry[0][SmartApiInputFields.price] if entry else None for entry in
#                      batch_data[SmartApiInputFields.best_5_buy_data]]
#         sell_quantity = [entry[0][SmartApiInputFields.quantity] if entry else None for entry in
#                          batch_data[SmartApiInputFields.best_5_sell_data]]
#         sell_price = [entry[0][SmartApiInputFields.price] if entry else None for entry in
#                       batch_data[SmartApiInputFields.best_5_sell_data]]
#
#         batch_data[TickMarketFeedColumns.bid_volume] = buy_quantity
#         batch_data[TickMarketFeedColumns.bid_price] = buy_price
#         batch_data[TickMarketFeedColumns.ask_price] = sell_price
#         batch_data[TickMarketFeedColumns.ask_volume] = sell_quantity
#
#         field_columns = [TickMarketFeedColumns.token,
#                          TickMarketFeedColumns.last_traded_price,
#                          TickMarketFeedColumns.last_traded_quantity,
#                          TickMarketFeedColumns.last_traded_timestamp,
#                          TickMarketFeedColumns.open_interest,
#                          TickMarketFeedColumns.bid_price,
#                          TickMarketFeedColumns.bid_volume,
#                          TickMarketFeedColumns.ask_price,
#                          TickMarketFeedColumns.ask_volume]
#         fields_df = batch_data[field_columns]
#         batch_data['fields'] = fields_df.to_dict('records')
#         final_columns = ['measurement', 'tags', 'time', 'fields']
#         df = batch_data[final_columns]
#         df[TickMarketFeedColumns.tag] = batch_data[TickMarketFeedColumns.tag]
#         return df

    # def convert_to_native_format(self, df:pd.DataFrame):
    #     if df is None or df.empty:
    #         return []
    #
    #     # Convert exchange_timestamp to datetime
    #     df['time'] = pd.to_datetime(df['exchange_timestamp'] // 1000, unit='s', utc=True)
    #
    #     # Prepare additional structure directly in DataFrame
    #     df['measurement'] = self.measurement  # Add measurement as a constant column
    #
    #     # Creating 'tags' dictionary more efficiently
    #     symbol_column = ['symbol']
    #     symbol_df = df[symbol_column]
    #     df['tags'] = symbol_df.to_dict('records')
    #
    #     # df[['buy_quantity', 'buy_price']] =  df['best_5_buy_data'].apply(self.extract_quantity_price)
    #     # df[['sell_quantity', 'sell_price']] = df['best_5_sell_data'].apply(self.extract_quantity_price)
    #
    #     buy_quantity = [entry[0]['quantity'] if entry else None for entry in df['best_5_buy_data']]
    #     buy_price = [entry[0]['price'] if entry else None for entry in df['best_5_buy_data']]
    #     sell_quantity = [entry[0]['quantity'] if entry else None for entry in df['best_5_sell_data']]
    #     sell_price = [entry[0]['price'] if entry else None for entry in df['best_5_sell_data']]
    #
    #     df['bid_volume'] = buy_quantity
    #     df['bid_price'] = buy_price
    #     df['ask_price'] = sell_price
    #     df['ask_volume'] = sell_quantity
    #
    #     # df[['bid_price', 'bid_volume']] = df['best_5_buy_data'].apply(lambda x: self.extract_buy_data(x)).apply(pd.Series)
    #     # df[['ask_price', 'ask_volume']] = df['best_5_sell_data'].apply(lambda x: self.extract_sell_data(x)).apply(pd.Series)
    #     # print(f"Completed Extracting best bid and ask price and volume {datetime.utcnow().time()}")
    #     # Select fields into a new DataFrame
    #     field_columns = ['token', 'last_traded_price', 'last_traded_quantity', 'last_traded_timestamp','open_interest',
    #                      'bid_price', 'bid_volume', 'ask_price', 'ask_volume']
    #     fields_df = df[field_columns]
    #     # Convert the fields DataFrame into a dictionary and assign back to df
    #     df['fields'] = fields_df.to_dict('records')
    #
    #     # Keep only necessary columns for the final dictionary
    #     final_columns = ['measurement', 'tags', 'time', 'fields']
    #     df = df[final_columns]
    #
    #     # Convert DataFrame to a list of dictionaries for database insertion
    #     points = df.to_dict('records')
    #     return points
    def convert_to_native_format(self, batch_data: pd.DataFrame) -> List[str]:
        if batch_data is None or batch_data.empty:
            return []

        # Set 'time' and 'measurement' columns pd.to_datetime(df[smart_api_input_fields.exchange_timestamp] // 1000, unit='s', utc=True)
        batch_data[TickMarketFeedColumns.time] = pd.to_datetime(batch_data[SmartApiInputFields.exchange_timestamp] // 1000, unit='s', utc=True)
        batch_data['measurement'] = AppConstants.Equity_Market_Data_Table

        # Create 'tags' column by directly mapping the 'tag' column into dictionaries
        batch_data['tags'] = batch_data[TickMarketFeedColumns.tag].apply(lambda x: {TickMarketFeedColumns.tag: x})

        # Initialize 'bid_price', 'bid_volume', 'ask_price', and 'ask_volume' with NaN
        batch_data[TickMarketFeedColumns.bid_price] = np.nan
        batch_data[TickMarketFeedColumns.bid_volume] = np.nan
        batch_data[TickMarketFeedColumns.ask_price] = np.nan
        batch_data[TickMarketFeedColumns.ask_volume] = np.nan

        # Identify rows where best_5_buy_data is not empty
        not_empty_buy_data = batch_data[SmartApiInputFields.best_5_buy_data].str.len() > 0

        # Process non-empty best_5_buy_data
        if not_empty_buy_data.any():
            first_buy_data = batch_data.loc[not_empty_buy_data, SmartApiInputFields.best_5_buy_data].str[0]
            first_buy_df = pd.DataFrame(first_buy_data.tolist(), index=first_buy_data.index)

            # Assign bid_price and bid_volume for non-empty best_5_buy_data
            batch_data.loc[not_empty_buy_data, TickMarketFeedColumns.bid_price] = first_buy_df[
                SmartApiInputFields.price]
            batch_data.loc[not_empty_buy_data, TickMarketFeedColumns.bid_volume] = first_buy_df[
                SmartApiInputFields.quantity]

        # Identify rows where best_5_sell_data is not empty
        not_empty_sell_data = batch_data[SmartApiInputFields.best_5_sell_data].str.len() > 0

        # Process non-empty best_5_sell_data
        if not_empty_sell_data.any():
            first_sell_data = batch_data.loc[not_empty_sell_data, SmartApiInputFields.best_5_sell_data].str[0]
            first_sell_df = pd.DataFrame(first_sell_data.tolist(), index=first_sell_data.index)

            # Assign ask_price and ask_volume for non-empty best_5_sell_data
            batch_data.loc[not_empty_sell_data, TickMarketFeedColumns.ask_price] = first_sell_df[
                SmartApiInputFields.price]
            batch_data.loc[not_empty_sell_data, TickMarketFeedColumns.ask_volume] = first_sell_df[
                SmartApiInputFields.quantity]

        # For rows where bid_price is missing, set bid_price to last_traded_price and bid_volume to -1
        bid_price_missing = batch_data[TickMarketFeedColumns.bid_price].isna()
        batch_data.loc[bid_price_missing, TickMarketFeedColumns.bid_price] = batch_data.loc[
            bid_price_missing, TickMarketFeedColumns.last_traded_price
        ].astype(float)
        batch_data.loc[bid_price_missing, TickMarketFeedColumns.bid_volume] = -1.0

        # For rows where ask_price is missing, set ask_price to last_traded_price and ask_volume to -1
        ask_price_missing = batch_data[TickMarketFeedColumns.ask_price].isna()
        batch_data.loc[ask_price_missing, TickMarketFeedColumns.ask_price] = batch_data.loc[
            ask_price_missing, TickMarketFeedColumns.last_traded_price
        ].astype(float)
        batch_data.loc[ask_price_missing, TickMarketFeedColumns.ask_volume] = -1.0

        # Define the 'fields' columns
        field_columns = [
            TickMarketFeedColumns.token,
            TickMarketFeedColumns.last_traded_price,
            TickMarketFeedColumns.last_traded_quantity,
            TickMarketFeedColumns.last_traded_timestamp,
            TickMarketFeedColumns.open_interest,
            TickMarketFeedColumns.bid_price,
            TickMarketFeedColumns.bid_volume,
            TickMarketFeedColumns.ask_price,
            TickMarketFeedColumns.ask_volume,
        ]

        # Create 'fields' column by converting the specified columns to dictionaries
        batch_data['fields'] = batch_data[field_columns].to_dict('records')

        # Prepare the final DataFrame
        final_columns = ['measurement', 'tags', 'time', 'fields']
        df_json = batch_data[final_columns]

        json_objects = df_json.to_dict(orient='records')
        return json_objects

    # def convert_to_native_format(self, batch_data: pd.DataFrame) -> List[str]:
    #     if batch_data is None or batch_data.empty:
    #         return []
    #
    #     # Set 'time' and 'measurement' columns
    #     batch_data[TickMarketFeedColumns.time] = pd.to_datetime(batch_data[SmartApiInputFields.exchange_timestamp], unit='ms', utc=True)
    #     batch_data['measurement'] = AppConstants.Equity_Market_Data_Table
    #
    #     # Create 'tags' column by directly mapping the 'tag' column into dictionaries
    #     batch_data['tags'] = batch_data[TickMarketFeedColumns.tag].apply(lambda x: {TickMarketFeedColumns.tag: x})
    #
    #     # Extract the first buy and sell data using vectorized operations
    #     first_buy_data = batch_data[SmartApiInputFields.best_5_buy_data].str[0].dropna()
    #     first_sell_data = batch_data[SmartApiInputFields.best_5_sell_data].str[0].dropna()
    #
    #     # Create DataFrames from the first buy and sell data
    #     first_buy_df = pd.DataFrame(first_buy_data.tolist(), index=first_buy_data.index)
    #     first_sell_df = pd.DataFrame(first_sell_data.tolist(), index=first_sell_data.index)
    #
    #     # Assign the required columns to batch_data using pandas indexing
    #     batch_data.loc[first_buy_df.index, TickMarketFeedColumns.bid_volume] = first_buy_df[SmartApiInputFields.quantity]
    #     batch_data.loc[first_buy_df.index, TickMarketFeedColumns.bid_price] = first_buy_df[SmartApiInputFields.price]
    #     batch_data.loc[first_sell_df.index, TickMarketFeedColumns.ask_volume] = first_sell_df[SmartApiInputFields.quantity]
    #     batch_data.loc[first_sell_df.index, TickMarketFeedColumns.ask_price] = first_sell_df[SmartApiInputFields.price]
    #
    #     # Define the 'fields' columns
    #     field_columns = [
    #         TickMarketFeedColumns.token,
    #         TickMarketFeedColumns.last_traded_price,
    #         TickMarketFeedColumns.last_traded_quantity,
    #         TickMarketFeedColumns.last_traded_timestamp,
    #         TickMarketFeedColumns.open_interest,
    #         TickMarketFeedColumns.bid_price,
    #         TickMarketFeedColumns.bid_volume,
    #         TickMarketFeedColumns.ask_price,
    #         TickMarketFeedColumns.ask_volume
    #     ]
    #
    #     # # Create 'fields' column by converting the specified columns to dictionaries
    #     # batch_data['fields'] = batch_data[field_columns].to_dict('records')
    #     #
    #     # # Prepare the final DataFrame
    #     # final_columns = ['measurement', 'tags', 'time', 'fields']
    #     # df = batch_data[final_columns]
    #     #
    #
    #
    #     return df
