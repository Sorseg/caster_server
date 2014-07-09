import json
import model


class Player:
    players = {}
    creature = None
    protocol = None
    username = None

    def send(self, msg: dict):
        return self.protocol.send(json.dumps(msg))

    def login(self, login, password):
        if login in self.players:
            return 'already logged in'
        creature = model.get_creature(login, password)
        if creature is None:
            return 'nocreature'

        self.creature = creature
        self.username = login
        self.players[self.username] = self

    def disconnected(self):
        self.players.pop(self.username, None)
        if self.creature:
            self.creature.save()
