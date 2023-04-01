import asyncio
from logging import Logger

from loguru import logger

from xparser.core.interfaces import *
from functools import lru_cache
from asyncio import AbstractEventLoop


class Pool(IPool):
    def __init__(self, loop):
        self.event_loop: AbstractEventLoop = loop
        self.workers: dict[str, IOrderParser] = {}
        self.tasks = []
        self.is_running = False
        self.logger = Logger(__name__)

    @lru_cache
    def get_init_data(self, name: str):
        import os
        res = {}
        for k, v in os.environ.items():
            if k.lower().startswith(name):
                k_c = k
                k_c = k_c.lower().replace(name+'_', '')
                res[k_c] = v
        return res

    async def run_workers(self):
        from xparser.database import Database
        from xparser.core.config import WORKERS
        await Database.init()
        from xparser.core.config import SYMBOLS
        logger.info(f"Start symbols {SYMBOLS}")
        if self.is_running:
            return
        logger.info(f'Start {len(WORKERS)} workers')
        for w in WORKERS:
            name = w.platform
            self.workers[name] = await w.create(loop=self.event_loop, **self.get_init_data(name))
        await self.subscribe_on_threads()
        await self.loop()

    async def subscribe_on_threads(self):
        from xparser.core.config import SYMBOLS
        for symbol in SYMBOLS:
            for i in self.workers.values():
                self.logger.info(f'Sub on {symbol}')
                await i.subscribe(symbol)
                await asyncio.sleep(1)

    async def loop(self):
        from asyncio import wait
        from xparser.database import Database
        for i in self.workers.values():
            self.tasks.append(self.event_loop.create_task(i.loop()))

        async def get_result():
            while True:
                await asyncio.sleep(0.2)
                res = await Database.proceed_database()
                print(res) if res else None
        self.tasks.append(self.event_loop.create_task(get_result()))
        await wait(self.tasks)
