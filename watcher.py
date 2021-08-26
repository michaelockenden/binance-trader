import json
import time

import websockets

from strategy import analyse


class Watcher:
    """
    Responsible for watching symbol candles and deciding when to order.
    """

    def __init__(self, base):
        self.base = base
        self.quote = "USDT"
        self.symbol = self.base + "/" + self.quote

        self._ws = None

        self._closes = []

        self.socket = f"wss://stream.binance.com:9443/ws/{self.base.lower()}usdt@kline_1m"

    async def listen(self):
        """Connects to websocket and constantly listens for any received messages"""
        self._ws = await websockets.connect(self.socket, ping_interval=None)

        async for message in self._ws:
            signal = await self._receive(message)
            if signal:
                yield signal

    async def _receive(self, message):
        """Handles received messages"""
        kline = json.loads(message)['k']

        if kline['x'] or True:
            # 'x' being True indicates the candle has closed

            print(time.ctime(time.time()), kline)
            self._closes.append(float(kline['c']))

            action = analyse(self._closes)

            return action

    @property
    def price(self):
        """Returns latest price"""
        return self._closes[-1]
