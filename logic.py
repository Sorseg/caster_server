import enum
import json
import random
import itertools
from actions import Actions
import geometry
from geometry import CoordDescriptor
import model

object_counter = itertools.count()

class LoginException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Player:
    players = {}
    creature = None
    protocol = None
    username = None
    site = None
    action = None
    visible_area = geometry.Area(model.SIGHT*2, circle=True)

    def send(self, msg: dict):
        return self.protocol.send(json.dumps(msg))

    def login(self, login, password):
        if login in self.players:
            raise LoginException('already logged in')
        creature = model.get_creature(login, password)
        if creature is None:
            raise LoginException('no creature')

        self.creature = creature
        self.username = login
        self.players[self.username] = self
        self.site = ActionSite(self)

    def disconnect(self):
        self.players.pop(self.username, None)
        if self.creature:
            self.creature.save()
        if self.site:
            self.site.disconnect()

    def send_environment(self):
        return self.site.send_environment()

    def send_objects(self):
        return self.site.send_objects()


class ActionSite(geometry.Area):
    sites = []

    class States(enum.Enum):
        ROAMING = 'roaming'
        FIGHTING = 'fighting'
        FAST_TRAVEL = 'travelling'

    def __init__(self, player: Player):
        self.player = player
        self.size = model.SIGHT*4+1
        super().__init__(self.size, center=self.player.creature.pos)
        self.state = self.States.FAST_TRAVEL
        self.sites.append(self)
        self.mobs = {}
        self.action_dispatcher = Actions(self.player, 'type')
        self.generate_enemies()

    def disconnect(self):
        self.sites.remove(self)

    def process_turn(self):
        yield from self.action_dispatcher(self.player.action)
        if random.randint(0, 4) < 1:
            self.generate_enemies()
        yield from self.send_environment()
        yield from self.send_objects()

    def generate_enemies(self):
        gen_perimeter = geometry.Area(model.SIGHT*2+3, center=self.center).perimeter()
        cells = list(c for c in gen_perimeter if model.get_pixel(c).ttype == 'floor')
        if not cells:
            return
        p = random.choice(cells)
        m = Mob(p, Mob.Type.zombie)
        self.mobs[m.id] = m

    def send_environment(self):
        env = {"what": "environment"}
        env.update(model.get_environment(self.player.creature))
        yield from self.player.send(env)

    def send_objects(self):
        obj = {"what": "objects"}
        obj.update(objects=self.get_object_dict())
        yield from self.player.send(obj)

    def get_object_dict(self):
        return {"{}".format(o.id): o.dict() for o in self.mobs.values()
                if o.pos.dst_sq(self.player.creature.pos) <= model.SIGHT*model.SIGHT}


class Mob:

    class Type(enum.Enum):
        zombie = 1

    def __init__(self, pos: tuple, type_):
        self.type = type_
        self._pos = pos
        self.hp = 20
        self.id = next(object_counter)

    def dict(self):
        return {
            "type": "zombie",
            "hp": self.hp,
            "pos": self.pos
        }

    pos = CoordDescriptor()





