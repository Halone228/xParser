from abc import ABC, abstractmethod
from xparser.dataclasses.datatypes import OrderBook, Symbol, Order
from functools import lru_cache


class IOrderParser(ABC):

    @classmethod
    @property
    @abstractmethod
    def platform(cls):
        ...

    @abstractmethod
    def subscribe(self, symbol: Symbol):
        ...

    @abstractmethod
    async def loop(self):
        ...

    @abstractmethod
    def __init__(self, **kwargs):
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
    def prepared_data(self, symbol: Symbol):
        from xparser.dataclasses import Platforms
        from xparser.database.models import Database
        spot_id = Platforms[self.platform].value
        u_id = spot_id * 40
        model = Database.table_factory((symbol.first + symbol.second).lower())
        return spot_id, u_id, model

    @staticmethod
    @abstractmethod
    def callback(self, response, *args):
        ...
