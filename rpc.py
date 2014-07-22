import json


class RPCMeta(type):
    def __new__(cls, name, bases, dict):
        return type.__new__(cls, name, bases, dict)

    def __init__(self, name, bases, dict):
        super().__init__(name, bases, dict)


class RPCBase(metaclass=RPCMeta):
    switch = 'what'

    def __call__(self, act):
        if not isinstance(act, dict):
            act = json.loads(act)
        what = act.pop(self.switch, None)
        if what is None:
            raise ValueError("{} is not registered here".format(what))

        return getattr(self, 'do_'+what)(**act)
