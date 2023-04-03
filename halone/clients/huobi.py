import loguru
import websockets
from typing import Callable
from json import dumps, loads


class HuobiWebsocket:
    urls = {
        'market': 'wss://api.huobi.pro/ws'
    }

    def __init__(self, loop, callback: Callable):
        import asyncio
        self.event_loop = loop
        self.__call = callback
        self.conn = websockets.connect(self.urls['market'])
        self.sub_topics = {}
        self.queue = asyncio.Queue()

    async def pong(self,conn,resp):
        if resp.get('ping'):
            await conn.send(dumps({"pong": resp.get("ping")}))
            return True
        return False

    async def loop(self):
        from gzip import decompress
        from json import loads
        async with self.conn as conn:
            while True:
                if not self.queue.empty():
                    await self.sub(conn, await self.queue.get())
                    self.queue.task_done()
                data = await conn.recv()
                response: dict = loads(decompress(data))
                p = await self.pong(conn, response)
                if p:
                    continue
                await self.__call(response)
    
    async def sub(self, conn, topic: str):
        from uuid import uuid4
        import json
        from gzip import decompress
        self.sub_topics[topic] = str(uuid4())
        await conn.send(json.dumps({
            'sub': topic,
            'id': self.sub_topics[topic]               
            }))
        p = True
        while p:
            resp = await conn.recv()
            resp = json.loads(decompress(resp))
            p = await self.pong(conn, resp)
        while True:
            if resp.get('tick'):
                await self.__call(resp)
            if resp.get('id'):
                break
            resp = await conn.recv()
        loguru.logger.info(resp)
        if resp["status"] != "ok":
            loguru.logger.error(f"Huobi error ({resp['err-msg']})")
    
    async def subscribe(self, topic: str):
        await self.queue.put(topic)
