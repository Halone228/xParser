from dataclasses import dataclass


@dataclass(slots=True)
class Symbol:
    first: str
    second: str

    def __str__(self):
        return f'{self.first}-{self.second}'

    def __hash__(self):
        return hash(self.first+self.second)


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
class CoinFee:
    fee: float
    network_info: dict
