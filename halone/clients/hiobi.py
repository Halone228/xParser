import websockets
from typing import Callable


class HuobiWebsocket:
    urls = {
        'market': 'wss://api.huobi.pro/ws'
    }

    def __init__(self, loop, callback: Callable):
        self.event_loop = loop
        self.__call = callback
        self.conn = websockets.connect(self.urls['market'])

    async def loop(self):
        from gzip import decompress
        import json
        async with self.conn as conn:
            while True:
                data = await conn.recv()
                response: dict = json.loads(decompress(data))
                print(response)
                ping = response.get('ping')
                if ping:
                    await conn.send(json.dumps({'pong': ping}))
                    continue
                await self.__call(response)
