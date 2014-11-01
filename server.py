#!/usr/bin/env python3.4
"""
TODO:
- connection timeout
"""
import asyncio
import json
import signal

import websockets
import logging
from websockets.server import WebSocketServerProtocol
import commands
from commands import Commands
from logic import Player

PORT = 7778
PROTOCOL_VERSION = 1


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    datefmt='%y-%m-%d:%H:%M:%S')


def interrupt(*args):
    print("Interrupted!")
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(loop.stop)

signal.signal(signal.SIGINT, interrupt)


def send_protocol_version(protocol: WebSocketServerProtocol):
    yield from protocol.send(json.dumps(dict(what="protocol", version=PROTOCOL_VERSION)))


@asyncio.coroutine
def handler(protocol: WebSocketServerProtocol, uri):
    player = Player(protocol)
    yield from send_protocol_version(protocol)
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


