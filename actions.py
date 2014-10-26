from asyncio.tasks import coroutine
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
        self.player.site.center = where

        yield from self.player.send(dict(
            what="walk",
            to=where
        ))

    @coroutine
    def do_attack(self, who):
        who = int(who)
        if who not in self.player.site.mobs:
            return self.player.send(dict(
                what="error",
                msg="unknown target to attack:{}".format(who)
            ))
        self.player.site.mobs.pop(who)
        yield from self.player.send(dict(
            what="event",
            type="death",
            who=who
        ))
