import asyncio
from functools import lru_cache
from itertools import chain

from xparser.dataclasses.datatypes import Symbol, OrderBook
from xparser.core.interfaces import IOrderParser
from xparser.database import Database, Spot
from typing import Iterable
from loguru import logger


class BinanceOrderParser(IOrderParser):
    async def subscribe(self, symbol: Symbol):
        self.symbols[symbol.first+symbol.second] = symbol

    async def loop(self):
        def generate_sockets(threads: Iterable[Symbol]):
            return [f'{(i.first+i.second).lower()}@depth5@100ms' for i in threads]
        while True:
            ms = self.socket.multiplex_socket(generate_sockets(self.symbols.values()))
            async with ms as acsocket:
                while True:
                    res = await acsocket.recv()
                    await self.callback(res)

    def __init__(self):

        from binance import BinanceSocketManager
        self.event_loop = None
        self.socket: BinanceSocketManager = None
        self.symbols = {}

    @classmethod
    async def create(cls, loop, api_key=None, api_secret=None):
        self = cls()
        from binance import BinanceSocketManager, AsyncClient
        self.event_loop = loop
        self.client = await AsyncClient.create(api_key=api_key, api_secret=api_secret, loop=self.event_loop)
        self.socket = BinanceSocketManager(self.client)
        return self

    @staticmethod
    @lru_cache
    def parse_symbol(stream: str):
        import re
        return re.search(r'^(\w+)@', stream).group(1).upper()

    async def callback(self, response: dict, *args):
        symbol = self.symbols[self.parse_symbol(response['stream'])]
        response = response['data']
        spot_id, symbol_id = self.prepared_data(symbol)
        await Database.add_to_database(
            spots=self.generate_spots(spot_id, symbol_id,
                                      (i[0] for i in response['asks'] if float(i[1])),
                                      (i[0] for i in response['bids'] if float(i[1])))
        )

    @classmethod
    @property
    def platform(cls):
        return "binance"


class KuCoinOrderParser(IOrderParser):
    async def subscribe(self, symbol: Symbol):
        await self.socket.subscribe(f'/spotMarket/level2Depth5:{symbol.first}-{symbol.second}')
        self.symbols[f'{symbol.first}-{symbol.second}'] = symbol
        await asyncio.sleep(2)

    async def loop(self):
        import asyncio
        from kucoin.asyncio.websockets import KucoinSocketManager
        while True:
            await asyncio.sleep(20)

    def __init__(self):
        self.symbols = {}

    @classmethod
    async def create(cls, loop, api_key=None, api_secret=None, api_passphrase=None):
        self = cls()
        from kucoin.client import Client
        from kucoin.asyncio.websockets import KucoinSocketManager
        self.client = Client(api_key=api_key, api_secret=api_secret, passphrase=api_passphrase)
        self.event_loop = loop
        self.socket = await KucoinSocketManager.create(loop=self.event_loop, client=self.client, callback=self.callback)
        return self

    @staticmethod
    @lru_cache
    def parse_symbol(topic: str):
        import re
        return re.search(r':(\w+-\w+)', topic).group(1)

    async def callback(self, response, *args):
        data = response['data']
        spot_id, symbol_id = self.prepared_data(self.symbols[self.parse_symbol(response['topic'])])
        await Database.add_to_database(
            spots=self.generate_spots(spot_id, symbol_id,
                                      (i[0] for i in data['asks'] if i[1] != '0'),
                                      (i[0] for i in data['bids'] if i[1] != '0'))
        )

    @classmethod
    @property
    def platform(cls):
        return "kucoin"


class HuobiParser:
    @classmethod
    def platform(cls):
        pass

    def subscribe(self, symbol: Symbol):
        self.symbols 

    async def loop(self):
        pass

    @staticmethod
    def callback(response, *args):
        

    def __init__(self,loop):
        from halone.clients import HuobiWebsocket
        self.huobi_socket = HuobiWebsocket(loop, self.callback)
        self.symbols = {}
