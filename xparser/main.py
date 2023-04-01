import asyncio


def run_dev():
    from dotenv import load_dotenv
    from os import getcwd
    from pathlib import Path
    from logging import basicConfig, Logger, INFO
    log = Logger(__name__, level=INFO)
    load_dotenv(Path(getcwd()).joinpath('main.env'))
    from xparser.core.impl import Pool
    loop = asyncio.get_event_loop()
    print('Start pool')
    pool = Pool(loop=loop)
    print('Run workers')
    loop.run_until_complete(pool.run_workers())
