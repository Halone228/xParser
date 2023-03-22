from dataclasses import dataclass
from xparser.dataclasses.interfaces import IOrderParser


@dataclass(slots=True)
class Symbol:
    first: str
    second: str


@dataclass(slots=True)
class Order:
    price: float
    amount: float


@dataclass(slots=True)
class OrderBook:
    bids: list[Order]
    asks: list[Order]


@dataclass(slots=True)
class PlatformOrder:
    platform: str
    book: OrderBook


@dataclass(slots=True)
class OrdersCluster:
    platforms_instance: dict[str, IOrderParser]
    orders_books: list[PlatformOrder]
