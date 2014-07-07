from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import logging

EXECUTOR = ThreadPoolExecutor(max_workers=4)
TIMEOUT = 15
MAX_TIME = 100


class Player:
    players = {}
    
    def __init__(self, handler):
        self.handler = handler
        self.login = None
    
    @classmethod
    def get_players(cls):
        return [p for p in cls.players.values()]


logic_functions = {}


def logic(func):
    """
    Registers function as action,
    which can be performed with request
    """
    logic_functions[func.__name__.lower()] = func
    return func


def send_environment(player):
    id = player.creature.loc_id or player.loc_id
    @locking(id)
    def _():
        with db.Handler() as h:
            loc = h.session.query(db.Location).get(id)
            env = dict(what = "environment",
                       location = id,
                       turn = loc.current_turn,
                       )
            env['cells'] = [c.info() for c in loc.cells.values()]
            env['objects'] = [o.info() for o in loc.objects.values()]
            player.handler.write_message(env)
            
def add_updater(loc_id, loop = None):
    args = [create_loc_updater(loc_id), 1000*TIMEOUT]
    if loop:
        args.append(loop)
    upd = tornado.ioloop.PeriodicCallback(*args)
    loc_containers[loc_id].updater = upd
    upd.start()

def check_update(player):
    #TODO: invoke turn update if all committed
    if not loc_containers[player.loc_id].updater:
        add_updater(player.loc_id)
        
def create_response(request, success = True, **kw):
    response = {"what":"response",
                "result":"success" if success else "fail"}
    for k in ['type', 'source', 'target', 'target_cell', 'time', 'duration']:
        if k in request:
            response[k] = request[k]
    if request['type'] == 'enter':
        loc_containers[request['loc_id']].new_objs.append(request['source'])
    response.update(kw)
    loc_containers[request['loc_id']].requests.append(response)
    
def create_loc_updater(id):
    def updater():
        @locking(id)
        def _():
            logging.debug("Updating location #{}".format(id))
            requests = loc_containers[id].requests
            loc_containers[id].requests = []
            
            current_times = defaultdict(int)
            for r in requests:
                s = r['source']
                new_time = current_times[s.id] + r['duration']
                
                if new_time > MAX_TIME:
                    create_response(r, success = False)
                r['time'] = current_times[s.id]
                current_times[s.id] += r['duration']
                
            requests = sorted(requests, key = lambda r: r['time'])
            #TODO: implement simultaneous actions
            for r in requests:
                try:
                    logic_functions[r['type'].lower()](r)
                except:
                    logging.exception("Error in logic function")
                logging.debug("Processing {!s}".format(r))
            with db.Handler() as h:
                l = h.get_location(id)
                responses = loc_containers[id].responses
                loc_containers[id].responses = []
                new_objs = []
                resp_json = {"what":"responses",
                             "responses" : responses,
                             "turn":l.current_turn}
                
                for obj in loc_containers[id].new_objs:
                    o = h.refresh(obj)
                    new_objs.append(o.info())
                loc_containers[id].new_objs = []
                resp_json['new_objects'] = new_objs
                l.current_turn += 1
                logging.info("Planning turn #{}".format(l.current_turn))
            for p in Player.get_players(id):
                p.handler.write_message(resp_json)
            
    return updater
    
def init(loop):
    with db.Handler() as h:
        for location in h.session.query(db.Location):
            if location.creatures:
                add_updater(location.id, loop)


######################### LOGIC ROUTINES ######################

@logic
def enter(request):
    with db.Handler() as h:
        l = h.get_location(request['loc_id'])
        s = h.refresh(request['source'])
        for cell in l.cells:
            space = s.space()
            if space.fits(cell, l):
                s.coords = cell
                s.loc_id = l.id
                create_response(request, target_cell = cell)
                break
        else:
            create_response(request, success = False)
            #TODO: Tell user and try again
        

                