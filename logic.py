import enum
import json
import random
from actions import Actions
import geometry
from geometry import CoordDescriptor
import model


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


class ActionSite(geometry.Area):
    sites = []

    class States(enum.Enum):
        ROAMING = 'roaming'
        FIGHTING = 'fighting'
        FAST_TRAVEL = 'travelling'

    def __init__(self, player: Player):
        self.player = player
        self.size = model.SIGHT*4
        super().__init__(self.size, center=self.player.creature.pos)
        self.state = self.States.FAST_TRAVEL
        self.sites.append(self)
        self.mobs = []
        self.action_dispatcher = Actions(self.player, 'type')
        self.generate_enemies()

    def disconnect(self):
        self.sites.remove(self)

    def process_turn(self):
        yield from self.action_dispatcher(self.player.action)
        if random.randint(0, 99) < 1:
            self.generate_enemies()
        yield from self.send_environment()

    def generate_enemies(self):
        p = random.choice(list(self.perimeter()))
        self.mobs.append(Mob(p, Mob.Type.zombie))

    def send_environment(self):
        env = {"what": "environment"}
        env.update(model.get_environment(self.player.creature))
        env.update(objects=self.get_object_dict())
        yield from self.player.send(env)

    def get_object_dict(self):
        return {"{},{}".format(*m.pos): m.dict() for m in self.mobs}


class Mob:

    class Type(enum.Enum):
        zombie = 1

    def __init__(self, pos: tuple, type_):
        self.type = type_
        self._pos = pos
        self.hp = 20

    def dict(self):
        return {
            "type": "zombie",
            "hp": self.hp
        }

    pos = CoordDescriptor()





