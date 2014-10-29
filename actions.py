from asyncio.tasks import coroutine
from geometry import Coord
from rpc import RPCBase
import errors


class Actions(RPCBase):

    def __init__(self, player, switch='what'):
        self.player = player
        self.switch = switch

    def do_walk(self, where):

        c = self.player.creature
        where = Coord(*map(int, where))
        if c.pos.dst_sq(where) > 2:
            yield from self.player.send(errors.WALKING_TOO_FAR)
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
            error = dict(errors.UNKNOWN_TARGET)
            error.update(target=who)
            return self.player.send(error)
        self.player.site.mobs.pop(who)
        yield from self.player.send(dict(
            what="event",
            type="death",
            who=who
        ))
