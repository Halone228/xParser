import asyncio
from functools import lru_cache
from itertools import chain

import loguru

from xparser.dataclasses.datatypes import Symbol
from xparser.core.interfaces import IOrderParser
from xparser.database import Database, Spot
from typing import Iterable
import loguru


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


class HuobiParser(IOrderParser):
    @classmethod
    async def create(cls, loop):
        self = cls(loop)
        return self

    @classmethod
    @property
    def platform(cls):
        return "huobi"

    async def subscribe(self, symbol: Symbol):
        from asyncio import sleep
        symbol_huobi = (symbol.first+symbol.second).lower()
        self.symbols[symbol_huobi] = symbol
        await self.huobi_socket.subscribe(f'market.{symbol_huobi}.bbo')
        await sleep(1)

    async def loop(self):
        await self.huobi_socket.loop()

    async def callback(self,response, *args):
        data = response['tick']
        spot_id, symbol_id = self.prepared_data(self.symbols[data['symbol']])
        await Database.add_to_database(
            spots=[
                Spot(
                    spot_id=spot_id,
                    symbol_id=symbol_id,
                    ask=True,
                    price=data['ask']
                ),
                Spot(
                    spot_id=spot_id,
                    symbol_id=symbol_id,
                    ask=False,
                    price=data['bid']
                )
            ]
        )

    def __init__(self,loop):
        from halone.clients import HuobiWebsocket
        self.huobi_socket = HuobiWebsocket(loop, self.callback)
        self.symbols = {}


class PoloniexParser(IOrderParser):
    @classmethod
    @property
    def platform(cls):
        return "poloniex"

    async def subscribe(self, symbol: Symbol):
        symb = f"{symbol.first}_{symbol.second}"
        self.symbols[symb] = symbol
        await self.socket.subscribe(symb)

    async def loop(self):
        await self.socket.loop()

    @classmethod
    async def create(cls, loop, **kwargs):
        return cls(loop)

    @loguru.logger.catch
    async def callback(self, response, *args):
        data_ = response['data']
        for data in data_:
            spot_id, symbol_id = self.prepared_data(self.symbols[data['symbol']])
            await Database.add_to_database(
                spots=(Spot(
                    spot_id=spot_id,
                    symbol_id=symbol_id,
                    price=i[0],
                    ask=i[1]
                ) for i in chain(
                    ((float(k[0]), True) for k in data['asks']),
                    ((float(k[0]), False) for k in data['bids'])
                ))
            )

    def __init__(self, loop):
        from halone.clients import PoloPublicWebsocket
        from asyncio import AbstractEventLoop
        self.socket = PoloPublicWebsocket(self.callback)
        self.symbols = {}
        self.event_loop: AbstractEventLoop = loop


class MXCParser(IOrderParser):

    def __init__(self):
        from halone.clients import MXCMarketWebsocket
        self.symbols = {}
        self.socket = MXCMarketWebsocket(self.callback)

    @classmethod
    @property
    def platform(cls):
        return "mxc"

    async def subscribe(self, symbol: Symbol):
        self.symbols[f"{symbol.first}{symbol.second}"] = symbol
        await self.socket.subscribe(f"{symbol.first}{symbol.second}")

    async def loop(self):
        await self.socket.loop()

    @classmethod
    async def create(cls, **kwargs):
        return cls()

    @loguru.logger.catch
    async def callback(self, response, *args):
        spot_id, symbol_id = self.prepared_data(
            self.symbols[response['s']]
        )
        response = response['d']
        await Database.add_to_database(
            spots=(
                Spot(
                    spot_id=spot_id,
                    symbol_id=symbol_id,
                    price=i[0],
                    ask=i[1]
                ) for i in chain(
                    ((float(k['p']), True) for k in response.get('asks', [])),
                    ((float(k['p']), False) for k in response.get('bids', []))
                )
            )
        )
