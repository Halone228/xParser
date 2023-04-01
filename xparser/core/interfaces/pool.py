from abc import ABC, abstractmethod


class IPool(ABC):
    @abstractmethod
    async def run_workers(self):
        ...

    @abstractmethod
    async def subscribe_on_threads(self):
        ...