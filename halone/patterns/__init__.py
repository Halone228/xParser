from .observer import *
from xparser.database.models import SpotResult
from typing import Iterable
from typing import TYPE_CHECKING


class AppStateObserverMixin(AsyncSubscriber):

    def __init__(self, publisher: "AppStatePublisherMixin"):
        publisher.add_subscriber(self)


class AppStatePublisherMixin(Publisher):
    state = True

    async def change_state(self):
        self.state = not self.state
        await self.notify_async()


class SpotResultObserver(AsyncSubscriber):

    @staticmethod
    def format_message(result: SpotResult):
        from xparser.core.config import Platforms, SymbolsEnum
        p1 = Platforms(result.spot_id1)
        p2 = Platforms(result.spot_id2)
        s = SymbolsEnum(result.symbol_id)
        return f"Профит в {s.name} {p1.name}->{p2.name}\n" \
               f"{result.price1}->{result.price2}\n" \
               f"{'Покупка' if result.ask else 'Продажа'}\n" \
               f"Профит: {result.benefit: .3f}"


class SpotResultPublisher(Publisher):
    best_result = None

    async def new_best_result(self, best_result: Iterable[SpotResult]):
        self.best_result = best_result
        await self.notify_async()
