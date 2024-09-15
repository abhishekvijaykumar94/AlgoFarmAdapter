# connection_manager.py
import pyotp
from SmartApi import SmartConnect
from algoLibs.utils.property_manager import PropertyManager


class SmartApiConnectionManager:

    def __init__(self, api_key, username=None, password=None, token=None):
        self.api_key = api_key
        if api_key is None or username is None or password is None or token is None:
            self.load_from_config()
        else:
            self.username = username
            self.password = password
            self.token = token
        self.smartConnect = SmartConnect(api_key=self.api_key)

    def load_from_config(self):
        self.username = PropertyManager.getValue('clientCode')
        self.password = PropertyManager.getValue('pwd')
        self.token = PropertyManager.getValue('token')

    def generate_session(self):
        data = self.smartConnect.generateSession(self.username,self.password,pyotp.TOTP(self.token).now())
        self.res = self.smartConnect.getProfile(data['data']['refreshToken'])
        self.feedToken = self.smartConnect.getfeedToken();
        return data,self.feedToken

    def refresh_token(self):
        # Code to refresh token
        pass



# This is just a starting point. Each class would need to be fleshed out with actual implementation details.
