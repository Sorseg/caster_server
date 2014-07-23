from collections import namedtuple


class Coord(namedtuple('Coord', 'x, y')):

    def __add__(self, other):
        x, y = other
        return Coord(self.x + x, self.y + y)

    def __sub__(self, other):
        x, y = other
        return Coord(self.x - x, self.y - y)

    def __truediv__(self, other):
        return Coord(self.x/other, self.y/other)

    def dst_sq(self, other):
        x1, y1 = self
        x2, y2 = other
        dx = x2 - x1
        dy = y2 - y1
        return dx*dx + dy*dy


class CoordDescriptor:

    def __set__(self, instance, value):
        instance._pos = value

    def __get__(self, instance, owner):
        return Coord(*instance._pos)



class Area(object):
    """Piece of space"""

    pos = CoordDescriptor()

    def __init__(self, size: int, pos: (tuple, Coord)=(0, 0), circle: bool=False):
        self._pos = pos
        self.size = size
        self.circle = circle
        if self.circle:
            self._cells = self._circle
        else:
            self._cells = self._square

    @property
    def center(self):
        r = self.size//2
        return self.pos + (r, r)

    @center.setter
    def center(self, val):
        r = self.size//2
        self.pos = Coord(*val) - (r, r)

    def __and__(self, other):
        l = self.pos.x + self.size < other.pos.x
        r = self.pos.x > other.pos.x + other.size
        t = self.pos.y + self.size < other.pos.y
        b = self.pos.y > other.pos.y + other.size
        return not any((l, r, t, b))

    def cells(self, pos=None):
        if self.size == 0:
            return set()
        if pos is None:
            pos = self.pos
            return self._cells(pos)

    def _square(self, pos):
        rng = range(self.size)
        return set(pos+(x, y) for x in rng for y in rng)

    def _circle(self, pos):
        sz = self.size - 1
        r = sz/2
        max_dst = r*r+1
        center = pos + Coord(sz, sz) / 2
        res = set(p for p in self._square(pos) if center.dst_sq(p) <= max_dst)
        return res


'''
class TerrainPiece(Area):
    def __init__(self, pos, size, map_data):
        super().__init__(size, pos, circle=True)
        self.terrain_dict = {}
        for x in range(pos_x - size, pos_x + size+1):
            for y in range(pos_y - size, pos_y + size+1):
                pixel = list(map_data[(x, y)])
                ttype = 'wall' if all(c < 200 for c in pixel) else 'floor'
                pixel.append(ttype)
                self.terrain_dict[(x, y)] = pixel

    def dict(self):
        return {"{},{}".format(*k): p for k, p in self.terrain_dict.items()}
'''