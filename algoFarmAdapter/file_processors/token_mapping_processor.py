import os

import pandas as pd
from datetime import datetime
from algoLibs import CommonUtils
from dateutil import parser as date_parser

class TokenMappingProcessor:
    def __init__(self, token_mapping_file_name, file_path=None):
        if file_path is None:
            self.token_mapping_path = CommonUtils.getFilePathFromDataDirectory(token_mapping_file_name)
        else:
            self.token_mapping_path = os.path.join(file_path,token_mapping_file_name)

        # Load and clean the token mapping data
        self.token_mapping = pd.read_csv(self.token_mapping_path, skip_blank_lines=True)
        self.clean_expiry_dates()
        self.update_date_column()

    def update_date_column(self):
        self.token_mapping['parsed_date'] = self.token_mapping['date'].apply(self.parse_dates)
        self.token_mapping['date'] = pd.to_datetime(self.token_mapping['parsed_date'], format='%Y-%m-%d')

    @staticmethod
    def parse_dates(date):
        try:
            return date_parser.parse(date)
        except (ValueError, TypeError):
            return None

    def clean_expiry_dates(self):
        """
        Cleans and standardizes the expiry dates in the token mapping DataFrame.
        """
        def parse_expiry_date(expiry_str):
            for fmt in ("%d-%b-%y", "%d%b%Y", "%Y-%m-%d", "%d%b%y"):
                try:
                    return datetime.strptime(expiry_str, fmt).strftime('%d%b%y')
                except (ValueError, TypeError):
                    continue
            return expiry_str  # Return the original string if no format matches

        self.token_mapping['expiry'] = self.token_mapping.apply(
            lambda row: parse_expiry_date(row['expiry']) if row['instrumenttype'] in ['OPTIDX', 'FUTIDX'] else row['expiry'],
            axis=1
        )

    def save_token_mapping(self):
        """
        Saves the cleaned token mapping DataFrame back to the CSV file.
        """
        self.token_mapping.to_csv(self.token_mapping_path, index=False)

    def get_option_tokens(self):
        filtered_token_df = self.token_mapping[self.token_mapping['instrumenttype'] == 'OPTIDX']
        return filtered_token_df['token'].unique()

    def get_equity_symbols(self):
        filtered_token_df = self.token_mapping[self.token_mapping['exch_seg'] == 'NSE']
        return filtered_token_df['symbol'].unique()

    def get_index_underlying_tokens(self):
        filtered_token_df = self.token_mapping[self.token_mapping['instrumenttype'] == 'AMXIDX']
        return filtered_token_df['token'].unique()

    def get_symbols_and_tokens(self):
        symbol_list = self.token_mapping['symbol'].tolist()
        token_list = self.token_mapping['token'].tolist()
        return symbol_list,token_list

    def get_token_to_symbol_dict(self):
        self.token_mapping.sort_values(by=['token', 'date'], ascending=[True, False], inplace=True)
        df = self.token_mapping.drop_duplicates(subset='token', keep='last')
        token_symbol_map = df.set_index('token')['symbol'].to_dict()
        return token_symbol_map

    def get_migration_token_to_symbol_dict(self, filter_date):
        valid_tokens = self.token_mapping[self.token_mapping['date'] <= filter_date]
        latest_tokens = valid_tokens.loc[valid_tokens.groupby('token')['date'].idxmax()]
        return dict(zip(latest_tokens['token'], latest_tokens['symbol']))

    def get_token_to_symbol_df(self):
        if not hasattr(self, 'processed_df'):
            self.processed_df = self.token_mapping.sort_values(by=['token', 'date'], ascending=[True, False])
            self.processed_df = self.processed_df.drop_duplicates(subset='token', keep='last')
        return self.processed_df[['token', 'symbol']]

    def get_tokens_by_criteria(self, exch_seg=None, instrumenttype=None):
        """
        Retrieves tokens based on specified criteria.
        """
        filtered_df = self.token_mapping
        if exch_seg:
            filtered_df = filtered_df[filtered_df['exch_seg'] == exch_seg]
        if instrumenttype:
            filtered_df = filtered_df[filtered_df['instrumenttype'] == instrumenttype]
        return filtered_df['token'].unique()
