#!/usr/bin/env python3.4
"""
TODO:
- connection timeout
"""
import asyncio
import signal

import websockets
import logging

PORT = 7778

logging.basicConfig(filename='caster.log',
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    datefmt='%y-%m-%d:%H:%M:%S')


def interrupt(*args):
    print("Exiting...")
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(loop.stop)

signal.signal(signal.SIGINT, interrupt)

@asyncio.coroutine
def handler(proto, uri):
    logging.info("CONNECTED TO {}".format(uri))
    while proto.open:
        message = yield from proto.recv()
        logging.debug("MSG RECEIVED:" + message)

    logging.info("DISCONNECTED {}".format(uri))


asyncio.get_event_loop().run_until_complete(websockets.serve(handler, '0.0.0.0', PORT))
asyncio.get_event_loop().run_forever()


