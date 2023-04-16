from binance.client import Client
from xparser.core.interfaces import IPlatformInfoGet
from xparser.dataclasses import Symbol, CoinFee
from functools import lru_cache


class BinanceStatus(IPlatformInfoGet):

    def __init__(self):
        self.client = Client()
        self.coins = None
        self.symbols = None

    def get_all_coins(self):
        return [i['coin'] for i in self.coins]

    def get_coin_info(self, coin: str):
        coin = coin.upper()
        for i in self.coins:
            if coin == i['coin']:
                return i
        return False

    def get_all_symbols(self):
        [Symbol(
            first=i['baseAsset'],
            second=i['quoteAsset']
        ) for i in self.symbols]

    @lru_cache
    def get_coin_fees(self, coin: str):
        return list(
            (
                CoinFee(
                    fee=i["withdrawFee"],
                    network_info=i
                )
                for i in self.get_coin_info(coin)['networkList'])
        )

    def get_symbol_info(self, symbol: Symbol):
        return self.client.get_isolated_margin_symbol(
            symbol=f"{symbol.first}{symbol.second}"
        )

    async def update(self):
        self.coins = self.client.get_all_coins_info()
        self.get_coin_fees.cache_clear()
        self.symbols = self.client.get_exchange_info()['symbols']

    def platform(cls):
        return "binance"
