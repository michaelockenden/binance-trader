import json
import time

import websockets

from strategy import BUY, SELL
from strategy import analyse


class Watcher:
    """
    Responsible for watching symbol candles and deciding when to order.
    """

    def __init__(self, symbol):
        self.base = symbol
        self.quote = "USDT"
        self.symbol = self.base + "/" + self.quote

        self._ws = None
        self._loop = None

        self._closes = []
        self._bought = False

        self.socket = f"wss://stream.binance.com:9443/ws/{symbol.lower()}usdt@kline_1m"

    async def listen(self, loop):
        self._ws = await websockets.connect(self.socket, ping_interval=None)
        self._loop = loop

        async for message in self._ws:
            signal = await self._receive(message)
            if signal:
                yield signal

    async def _receive(self, message):
        kline = json.loads(message)['k']

        if kline['x'] or True:
            # 'x' being True indicates the candle has closed

            print(time.ctime(time.time()), kline)
            self._closes.append(float(kline['c']))

            action = analyse(self._closes)

            if action == BUY and not self._bought:
                self._bought = True
                return action

            if action == SELL and self._bought:
                self._bought = False
                return action
