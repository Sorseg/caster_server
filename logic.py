import json
import model


class LoginException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Player:
    players = {}
    creature = None
    protocol = None
    username = None

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

    def disconnected(self):
        self.players.pop(self.username, None)
        if self.creature:
            self.creature.save()
