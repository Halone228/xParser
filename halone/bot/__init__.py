from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from halone.patterns import SpotResultObserver, SpotResultPublisher
from xparser.database import SpotResult, Users
from os import getenv
from xparser.database import Database


bot = Bot(getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ConcreteObserver(SpotResultObserver):

    async def update(self, publisher: SpotResultPublisher):
        results = publisher.best_result
        for result in results:
            await self.send_subed(self.format_message(result))

    async def send_subed(self, message):
        users = await Users.get_all_subed()
        for user in users:
            await dp.bot.send_message(user.user_id, message)


class DebugObserver(SpotResultObserver):
    async def update(self, publisher: SpotResultPublisher):
        result = max(publisher.best_result, key=lambda res: res.benefit)
        await dp.bot.send_message(getenv("DEBUG_CHAT"), self.format_message(result))


DebugObserver(Database.publisher)
