import json
from logic import Player
import model


model.init()
commands = {}


def cmd(func):
    """ Registers a function as a command """
    commands[func.__name__] = func
    return func  


def do(protocol: Player, message: str):
    js = json.loads(message)
    command = js.pop('what')
    return commands[command](protocol, **js)


def send_environment(player):
    env = {"what": "environment"}
    env.update(model.get_environment(player.creature))
    yield from player.send(env)

#COMMANDS:


@cmd
def login(player: Player, login, password):

    creature = model.get_creature(login, password)
    if creature is None:
        yield from player.protocol.send(json.dumps({"what": "nocreature"}))
        return
    player.creature = creature
    player.username = login
    crt = {"what": "creature"}
    crt.update(creature.dict())
    yield from player.send(crt)
    yield from send_environment(player)


@cmd
def walk(player: Player, where):
    c = player.creature
    #TODO: add validation
    c.pos_x, c.pos_y = where
    yield from player.send(dict(
        what="walk",
        to=where
    ))
    yield from send_environment(player)


'''
@cmd
def login(handler, login, passw):
    player = handler.player 
    send = handler.write_message
    if player.login:
        send(error("Already logged in"))
        return
    #TODO: If one of the creatures has entered domain
    #it should automaticaly be chosen
    with db.Handler() as h:
        creatures = h.login(login, passw)
        if creatures == None:
            send(fail("Login and/or pass are wrong"))
            return
        elif not creatures:
            send(fail("Login {} has no creatures".format(login)))
            return
        
        if login in player.players:
            send(fail("Already logged in"))
            return
        player.login = login
        player.players[login] = player
        player.creatures = {c.id:c for c in creatures}
        
        send({"what":"login",
              "creatures":[c.info() for c in creatures]})

@cmd
def join(handler, crid):
    player = handler.player
    
    if not player.login:
        handler.write_message(error("not logged in"))
        return
    
    if player.loc_id:
        handler.write_message(error("Already joined"))
        return
    
    with db.Handler() as h:
        player.creature = h.refresh(player.creatures[crid])
        if any(c == None for c in player.creature.coords) or not player.creature.loc_id:
            requests.ENTER(player, 1)
        else:
            player.loc_id = player.creature.loc_id
        handler.write_message({"what":"joined", "crid":crid})
        logic.send_environment(player)

@cmd 
def request(handler, **kw):
    pass
'''
