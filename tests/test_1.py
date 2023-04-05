from halone.clients import MXCMarketWebsocket

async def test1():
    import asyncio
    loop = asyncio.get_event_loop()
    async def call(resp):
        print(resp)
    huobi = MXCMarketWebsocket(call)
    print(2)
    await huobi.subscribe('BTCUSDT')
    print(1)
    await huobi.loop()


def run_tests():
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test1())
