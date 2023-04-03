from websockets import connect


class PoloPublicWebsocket:
    public_ip = "wss://ws.poloniex.com/ws/public"

    def __init__(self, callback):
        self.symbols = []
        self.p_len = 0
        self.conn = connect(self.public_ip)
        self.__call = callback
        from json import dumps
        self.ping_str = dumps({'event': 'ping'})

    async def sub_book(self, conn, symbols: list[str]):
        from json import dumps
        str = dumps(
            {
                'event': 'subscribe',
                'channel': ['book'],
                'symbols': symbols,
                'depth': 5
            }
        )
        from loguru import logger
        logger.info(str)
        await conn.send(str)

    async def subscribe(self, symbol: str):
        self.symbols.append(symbol)

    async def ping(self, conn):
        await conn.send(self.ping_str)

    async def loop(self):
        from json import loads
        async with self.conn as conn:
            await self.ping(conn)
            i = 0
            while True:
                if self.p_len < len(self.symbols):
                    await self.sub_book(conn, self.symbols[self.p_len-1 if self.p_len > 0 else 0:])
                    self.p_len = len(self.symbols)
                response = loads(await conn.recv())
                if response.get('event'):
                    continue
                await self.__call(response)
                i += 1
                if i > 100:
                    await self.ping(conn)

