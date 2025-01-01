from algoLibs.utils.property_manager import PropertyManager
from algoLibs import AppConstants
from algoFarmAdapter.file_processors.token_list_generator import TokenListGenerator
from algoFarmAdapter.market_data import InstrumentDataFetcher, MarketDataFetcher
from algoFarmAdapter.market_data.expiry_calculator import ExpiryCalculator

class SmartApiMarketDataSubscriber():

    def get_token_subscription_list(self):
        # instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        instrument_url = PropertyManager.getValue(AppConstants.INSTRUMENT_URL)
        instrument_data_fetcher = InstrumentDataFetcher(instrument_url)
        market_data_fetcher = MarketDataFetcher()
        expiry_calculator = ExpiryCalculator(instrument_data_fetcher, market_data_fetcher)
        token_list_generator = TokenListGenerator(instrument_data_fetcher, expiry_calculator)
        token_list = token_list_generator.generate_tokens()
        return token_list