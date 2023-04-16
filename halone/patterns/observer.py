from abc import ABC, abstractmethod
from typing import Union


class Publisher:
    instance = None

    def __init__(self):
        self.subscribers: list["Subscriber"] = []
        self.async_subscribers: list["AsyncSubscriber"] = []

    def add_subscriber(self, sub: "Subscriber"):
        self.subscribers.append(sub)

    def add_async_subscriber(self, sub: "AsyncSubscriber"):
        self.async_subscribers.append(sub)

    def notify(self):
        for i in self.subscribers:
            i.update(self)

    async def notify_async(self):
        for i in self.async_subscribers:
            await i.update(self)


class Subscriber(ABC):
    def __init__(self, publisher: Publisher):
        publisher.add_subscriber(self)

    @abstractmethod
    def update(self, publisher):
        ...


class AsyncSubscriber(ABC):
    def __init__(self, publisher: Publisher):
        publisher.add_async_subscriber(self)

    @abstractmethod
    async def update(self, publisher):
        ...


