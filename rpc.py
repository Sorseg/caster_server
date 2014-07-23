import json


class RPCBase:
    switch = 'what'

    def __call__(self, act):
        if not isinstance(act, dict):
            act = json.loads(act)
        what = act.pop(self.switch, None)
        if what is None:
            raise ValueError("{} is not registered in {}".format(what, self))

        return getattr(self, 'do_'+what)(**act)
