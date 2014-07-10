from collections import namedtuple
import math


class Coord(namedtuple('Coord', 'x, y')):

    def __add__(self, other):
        x, y = other
        return Coord(self.x + x, self.y + y)

    def __sub__(self, other):
        x, y = other
        return Coord(self.x - x, self.y - y)

    def __truediv__(self, other):
        return Coord(self.x/other, self.y/other)



def dst_sq(p1, p2):
    dx = p2[0]-p1[0]
    dy = p2[1]-p1[1]
    return dx*dx+dy*dy


class TerrainPiece:
    def __init__(self, pos, size, map_data):
        pos_x, pos_y = pos
        self.terrain_dict = {}
        for x in range(pos_x - size, pos_x + size+1):
            for y in range(pos_y - size, pos_y + size+1):
                pixel = list(map_data[(x, y)])
                ttype = 'wall' if all(c < 200 for c in pixel) else 'floor'
                pixel.append(ttype)
                self.terrain_dict[(x, y)] = pixel

    def dict(self):
        return {"{},{}".format(*k): p for k, p in self.terrain_dict.items()}


class Area(object):
    """Piece of space"""

    def __init__(self, pos, size, circle=False):
        self.pos = Coord(*pos)
        self.size = size
        self.circle = circle
        if self.circle:
            self._cells = self._circle
        else:
            self._cells = self._square

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
        print(r, center, max_dst)
        res = set(p for p in self._square(pos) if dst_sq(p, center) <= max_dst)
        return res
