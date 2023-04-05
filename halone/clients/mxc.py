from websockets import connect, ConnectionClosedOK
from json import dumps, loads
from loguru import logger


class MXCMarketWebsocket:
    public_url = 'wss://wbs.mexc.com/ws'

    def __init__(self, callback):
        self.symbols = []
        self.__call = callback
        self.conn = connect(self.public_url)

    async def subscribe(self, symbol: str):
        self.symbols.append(symbol)

    async def sub(self, conn):
        msg = dumps(
            {
                "method": "SUBSCRIPTION",
                "params": [
                    f"spot@public.limit.depth.v3.api@{i}@10" for i in self.symbols
                ]
            }
        )
        logger.info(msg)
        await conn.send(msg)

    async def ping(self,conn):
        await conn.send(dumps({"method":"PING"}))

    async def loop(self):
        while True:
            try:
                async with self.conn as conn:
                    await self.sub(conn)
                    i = 0
                    while True:
                        resp = loads(await conn.recv())
                        if resp.get('msg'):
                            if resp.get('msg') == 'PONG':
                                continue
                            logger.info(resp.get('msg'))
                            continue
                        await self.__call(resp)
                        i += 1
                        if i > 70:
                            await self.ping(conn)
            except ConnectionClosedOK as e:
                logger.info('24h spend, open new connection')
