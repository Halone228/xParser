from os import getenv
from enum import Enum, auto
import xparser.core.impl.worker
from xparser.core.interfaces import IOrderParser
from xparser.dataclasses import Symbol


class Platforms(Enum):
    binance = auto()
    kucoin = auto()
    huobi = auto()


SYMBOLS = list((Symbol(first=i.split('-')[0].strip(), second=i.split('-')[1]) for i in getenv('SYMBOLS').split(';') if i))
SymbolsEnum = Enum(
    'SymbolsEnum',
    {f'{i.first}-{i.second}': auto() for i in SYMBOLS}
)

WORKERS = IOrderParser.__subclasses__()



