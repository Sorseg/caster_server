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

    def send_environment(self):
        env = {"what": "environment"}
        env.update(model.get_environment(self.creature))
        yield from self.send(env)

    def disconnect(self):
        self.players.pop(self.username, None)
        if self.creature:
            self.creature.save()
        if self.site:
            self.site.disconnect()


class ActionSite(geometry.Area):
    sites = []

    class States(enum.Enum):
        ROAMING = 'roaming'
        FIGHTING = 'fighting'
        FAST_TRAVEL = 'travelling'

    def __init__(self, player: Player):
        self.player = player
        self.size = model.SIGHT*4
        super().__init__(self.size)
        self.state = self.States.FAST_TRAVEL
        self.sites.append(self)
        self.mobs = []
        self.action_dispatcher = Actions(self.player, 'type')

    def disconnect(self):
        self.sites.remove(self)

    def process_turn(self):
        self.generate_enemies()
        return self.action_dispatcher(self.player.action)

    def generate_enemies(self):
        if random.randint(0, 99) < 1:
            pos = (500, 500) #NO!
            self.mobs.append(Mob(Mob.Type.zombie, pos))


class Mob:

    class Type(enum.Enum):
        zombie = 1

    def __init__(self, pos, type):
        self.type = type
        self._pos = pos

    pos = CoordDescriptor()





