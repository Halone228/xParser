from os import getenv
from enum import Enum, auto
import xparser.core.impl.worker
from xparser.core.interfaces import IOrderParser
from xparser.dataclasses import Symbol


Platforms = Enum("Platforms", {
    i.platform: auto()
    for i in IOrderParser.__subclasses__()
})


SYMBOLS = [Symbol(first=i.split('-')[0].strip(), second=i.split('-')[1]) for i in getenv('SYMBOLS').split(';') if i]
SymbolsEnum = Enum(
    'SymbolsEnum',
    {f'{i.first}-{i.second}': auto() for i in SYMBOLS}
)

WORKERS = IOrderParser.__subclasses__()



