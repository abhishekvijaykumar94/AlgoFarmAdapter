# instrument_data_fetcher.py
import numpy as np
# instrument_data_manager.py
import pandas as pd
import json
import urllib.request as req

class InstrumentDataFetcher:
    def __init__(self, instrument_url):
        self.instrument_url = instrument_url
        self.token_df = None

    def fetch_instrument_data(self):
        response = req.urlopen(self.instrument_url)
        instrument_list = json.loads(response.read())
        self.token_df = pd.DataFrame.from_dict(instrument_list)
        self.update_instrument_type()
        return self.token_df

    def update_instrument_type(self):
        if self.token_df is not None:
            self.token_df['instrumenttype'] = self.token_df['instrumenttype'].replace('', np.nan)
            # Fill NaN values with 'EQ'
            self.token_df['instrumenttype'] = self.token_df['instrumenttype'].fillna('EQ')
