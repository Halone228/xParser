from abc import ABC, abstractmethod
from itertools import chain
from typing import Iterable
from xparser.database import Spot
from xparser.dataclasses.datatypes import OrderBook, Symbol, Order
from functools import lru_cache


class IOrderParser(ABC):

    @classmethod
    @property
    @abstractmethod
    def platform(cls):
        ...

    @abstractmethod
    async def subscribe(self, symbol: Symbol):
        ...

    @abstractmethod
    async def loop(self):
        ...

    @abstractmethod
    async def create(self,**kwargs):
        ...

    @staticmethod
    def parse_book(to_parse: dict):
        return OrderBook(
            bids=list(map(lambda a: Order(
                price=a[0],
                amount=a[1]
            ), to_parse.get('bids'))),

            asks=list(map(lambda a: Order(
                price=a[0],
                amount=a[1]
            ), to_parse.get('asks')))
        )

    @lru_cache
    def prepared_data(self, symbol: Symbol) -> tuple[int, int]:
        from xparser.core.config import Platforms, SymbolsEnum
        spot_id = Platforms[self.platform].value
        symbol_id = SymbolsEnum[f'{symbol.first}-{symbol.second}'].value
        return spot_id, symbol_id

    @staticmethod
    def generate_spots(spot_id, symbol_id, asks: Iterable[float], bids: Iterable[float]):
        return (
            Spot(
                spot_id=spot_id,
                symbol_id=symbol_id,
                price=i[0],
                ask=i[1]
            ) for i in chain(
                ((float(k), True) for k in asks),
                ((float(k), False) for k in bids)
            )
        )

    @staticmethod
    @abstractmethod
    def callback(self, response, *args):
        ...
