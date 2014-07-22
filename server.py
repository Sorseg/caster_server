#!/usr/bin/env python3.4
"""
TODO:
- connection timeout
"""
import asyncio
import signal

import websockets
import logging
import commands
from commands import Commands
from logic import Player

PORT = 7778

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    datefmt='%y-%m-%d:%H:%M:%S')


def interrupt(*args):
    print("Interrupted!")
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(loop.stop)

signal.signal(signal.SIGINT, interrupt)


@asyncio.coroutine
def handler(protocol, uri):
    player = Player()
    player.protocol = protocol
    command_dispatcher = Commands(player)
    while protocol.open:
        message = yield from protocol.recv()
        if message is None:
            break
        try:
            res = yield from command_dispatcher(message)
        except Exception as e:
            logging.exception("Message:{!r}".format(message))
        else:
            logging.debug("command result:{}".format(res))
    command_dispatcher.disconnect()
    logging.info("DISCONNECTED {}".format(uri))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(websockets.serve(handler, '0.0.0.0', PORT))
    asyncio.get_event_loop().run_forever()


