from abc import ABC, abstractmethod
from xparser.dataclasses.datatypes import OrderBook, Symbol, Order


class IOrderParser(ABC):

    @classmethod
    @property
    @abstractmethod
    def platform(cls):
        ...

    @abstractmethod
    async def get_order_book(self, symbol: Symbol) -> OrderBook:
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

    @staticmethod
    @abstractmethod
    def callback(self, *args, **kwargs):
        ...
