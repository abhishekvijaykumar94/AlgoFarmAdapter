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
        self.smart_connect = SmartConnect(api_key=self.api_key)

    def load_from_config(self):
        self.username = PropertyManager.getValue('clientCode')
        self.password = PropertyManager.getValue('pwd')
        self.token = PropertyManager.getValue('token')

    def generate_session(self):
        data = self.smart_connect.generateSession(self.username,self.password,pyotp.TOTP(self.token).now())
        self.res = self.smart_connect.getProfile(data['data']['refreshToken'])
        self.feed_token = self.smart_connect.getfeedToken()
        return data,self.feed_token

    def refresh_token(self):
        # Code to refresh token
        pass



# This is just a starting point. Each class would need to be fleshed out with actual implementation details.
