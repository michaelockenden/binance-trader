import json
from abc import ABC, abstractmethod

import numpy
import talib
import websockets

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


class Watcher(ABC):
    """
    Responsible for watching symbol candles and deciding when to order.
    """

    def __init__(self, symbol):
        self.SYMBOL = symbol + "/USDT"

        self._ws = None
        self._loop = None

        self._closes = []
        self._bought = False

        self.SOCKET = f"wss://stream.binance.com:9443/ws/{symbol.lower()}usdt@kline_1m"

    async def listen(self, loop):
        self._ws = await websockets.connect(self.SOCKET, ping_interval=None)
        self._loop = loop

        async for message in self._ws:
            await self._receive(message)

    async def _receive(self, message):
        kline = json.loads(message)['k']
        if kline['x']:
            print(kline)
            self._closes.append(float(kline['c']))

            if len(self._closes) > RSI_PERIOD:
                np_closes = numpy.array(self._closes)
                rsi = talib.RSI(np_closes, RSI_PERIOD)
                print(rsi)
                return await self._check(rsi[-1])

    async def _check(self, rsi):
        if rsi > RSI_OVERBOUGHT:
            if self._bought:
                print("==SELL==")
                if await self._order("sell"):
                    self._bought = False
                    return True
                else:
                    return False

        elif rsi < RSI_OVERSOLD:
            if not self._bought:
                print("==BUY==")
                if await self._order("buy"):
                    self._bought = True
                    return True
                else:
                    return False

    @abstractmethod
    async def _order(self, side):
        pass
