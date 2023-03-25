from xparser.dataclasses.datatypes import Symbol, OrderBook, Order
from xparser.dataclasses import Platforms
from xparser.dataclasses.interfaces import IOrderParser
from xparser.database.models import Database

class BinanceOrderParser(IOrderParser):
    def subscribe(self, symbol: Symbol):
        from binance.enums import WEBSOCKET_DEPTH_20
        self.symbols[Symbol.first+Symbol.second] = Symbol
        self.socket.depth_socket(symbol.first+symbol.second, interval=100)

    async def loop(self):
        async with self.socket as acsocket:
            while True:
                res = await acsocket.recv()
                await self.callback(res)

    def __init__(self, api_key, api_secret):
        from binance import BinanceSocketManager, AsyncClient
        import asyncio
        self.symbols = {}
        self.client = asyncio.run(AsyncClient.create(api_key=api_key, api_secret=api_secret))
        self.socket: BinanceSocketManager = BinanceSocketManager(self.client)

    async def callback(self, response: dict, *args):
        symbol = self.symbols[response['s']]
        spot_id, u_id, model = self.prepared_data(symbol)
        for i in response['a']:
            model(
                unique_id=u_id,
                price=i[0],
                ask=True,
                spot_id=spot_id
            ).save()
            u_id += 1
        for i in response['b']:
            model(
                unique_id=u_id,
                price=i[0],
                ask=True,
                spot_id=spot_id
            ).save()
            u_id += 1

    @classmethod
    @property
    def platform(cls):
        return "binance"


class KuCoinOrderParser(IOrderParser):
    def __init__(self,api_key, api_secret, api_passphrase, loop):
        from kucoin.client import Client
        from kucoin.asyncio.websockets import KucoinSocketManager
        import asyncio
        self.client = Client(api_key=api_key, api_secret=api_secret, passphrase=api_passphrase)
        self.loop = loop
        self.socket = KucoinSocketManager.create(loop=self.loop, client=self.client)

    async def get_order_book(self, symbol: Symbol) -> OrderBook:
        res = self.client.get_order_book(f'{symbol.first}-{symbol.second}')
        return self.parse_book(res)

    async def callback(self, response, *args):
        pass
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
