from abc import ABC, abstractmethod
from xparser.dataclasses import Symbol


class IPlatformInfoGet(ABC):
    @abstractmethod
    def get_all_coins(self):
        ...

    @abstractmethod
    def get_all_symbols(self):
        ...

    @abstractmethod
    def get_coin_fees(self, coin: str):
        ...

    @abstractmethod
    def get_symbol_info(self, symbol: Symbol):
        ...

    @abstractmethod
    def update(self):
        ...

    @classmethod
    @property
    @abstractmethod
    def platform(cls):
        ...
