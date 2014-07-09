import json


class Player:
    creature = None
    protocol = None

    def send(self, msg: dict):
        return self.protocol.send(json.dumps(msg))