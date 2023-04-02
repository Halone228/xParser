from halone.clients.hiobi import HuobiWebsocket

async def test1():
    import asyncio
    loop = asyncio.get_event_loop()
    async def call(resp):
        print(resp)
    huobi = HuobiWebsocket(loop, call)
    await huobi.subscribe('market.btcusdt.bbo')
    await huobi.loop()


def run_tests():
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test1())
