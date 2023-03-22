from xparser.dataclasses.datatypes import Symbol, OrderBook, Order
from xparser.dataclasses.interfaces import IOrderParser


class BinanceOrderParser(IOrderParser):
    async def get_order_book(self, symbol: Symbol) -> OrderBook:
        from binance.enums import WEBSOCKET_DEPTH_20
        self.socket.depth_socket(symbol.first+symbol.second, WEBSOCKET_DEPTH_20)
        async with self.socket as acsocket:
            while True:
                res = await acsocket.recv()
                self.callback(res)

    def __init__(self, api_key, api_secret):
        from binance import BinanceSocketManager, AsyncClient
        import asyncio
        self.client = asyncio.run(AsyncClient.create(api_key=api_key, api_secret=api_secret))
        self.socket: BinanceSocketManager = BinanceSocketManager(self.client)

    def callback(self, response: dict):



    @classmethod
    @property
    def platform(cls):
        return "binance"


class KuCoinOrderParser(IOrderParser):
    def __init__(self,api_key, api_secret, api_passphrase):
        from kucoin.client import Client
        self.client = Client(api_key=api_key, api_secret=api_secret, passphrase=api_passphrase)

    async def get_order_book(self, symbol: Symbol) -> OrderBook:
        res = self.client.get_order_book(f'{symbol.first}-{symbol.second}')
        return self.parse_book(res)

    @classmethod
    @property
    def platform(cls):
        return "kucoin"


class HuobiParser(IOrderParser):
    def __init__(self,access_key, secret_key):
        from huobi.client.market import MarketClient, DepthStep
        self.client = MarketClient()
        self.depth_step = DepthStep

    async def get_order_book(self, symbol: Symbol) -> OrderBook:
        res = self.client.sub_pricedepth()
        return self.parse_book(res.get('tick'))
