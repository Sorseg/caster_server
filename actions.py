from geometry import Coord
from rpc import RPCBase


class Actions(RPCBase):

    def __init__(self, player, switch='what'):
        self.player = player
        self.switch = switch

    def do_walk(self, where):

        c = self.player.creature
        where = Coord(*map(int, where))
        if c.pos.dst_sq(where) > 2:
            yield from self.player.send(dict(
                what="error",
                msg="Walking too far"
            ))
            return

        c.pos = where

        yield from self.player.send(dict(
            what="walk",
            to=where
        ))
        yield from self.player.send_environment()
