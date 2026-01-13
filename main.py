from pygg import GGClient
from config import uin, password
import asyncio


class FastGG(GGClient):
    pass

if __name__ == '__main__':
    asyncio.run(FastGG(uin, password).connect(reconnect=False))
