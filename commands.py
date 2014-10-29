import json
import errors
from logic import Player, LoginException
from rpc import RPCBase


class Commands(RPCBase):

    def __init__(self, player: Player):
        self.player = player

    def do_login(self, login, password):

        try:
            self.player.login(login, password)
        except LoginException as e:
            yield from self.player.protocol.send(json.dumps(
                errors.LOGIN_FAIL
            ))
            return

        crt = dict(what="creature")
        crt.update(self.player.creature.dict())
        yield from self.player.send(crt)
        yield from self.player.send_environment()
        yield from self.player.send_objects()

    def do_action(self, **action):
        self.player.action = action
        return self.player.site.process_turn()

    def disconnect(self):
        if self.player:
            self.player.disconnect()
            self.player = None
