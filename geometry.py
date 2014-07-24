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

    def dst_sq(self, other):
        x1, y1 = self
        x2, y2 = other
        dx = x2 - x1
        dy = y2 - y1
        return dx*dx + dy*dy


class CoordDescriptor:

    def __init__(self, name='_pos'):
        self.name = name

    def __set__(self, instance, value):
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return Coord(*getattr(instance, self.name, (0, 0)))


class Line:

    start = CoordDescriptor('_start')
    end = CoordDescriptor('_end')

    def __init__(self, start, end=None):
        if end is None:
            self.start = (0, 0)
            self.end = start
        else:
            self.start = start
            self.end = end

    def cells(self, pos=None):
        """
        :return: generator of all cells belonging to this line
        computed by Bresenham's line algorithm
        """
        if pos is None:
            pos = self.start
        else:
            pos = Coord(*pos)
        d = self.end - self.start
        steep = abs(d.y) > abs(d.x)

        #if d.x == 0:
        #    return (pos+(0, i) for i in range(d.y))
        max_l = max(abs(i) for i in d)
        min_l = min(abs(i) for i in d)
        for i in range((d.y if steep else d.x) + 1):
            if not steep:
                yield pos+(i, i*min_l//max_l)
            else:
                yield pos+(i*min_l//max_l, i)


class Area(object):
    """Piece of space"""

    pos = CoordDescriptor()

    def __init__(self, size: int, pos: tuple=(0, 0), circle: bool=False, center: (tuple, Coord)=None):
        """
        :param center overrides pos
        """
        self._pos = pos

        self.size = size
        self.circle = circle
        if self.circle:
            self._cells = self._circle
        else:
            self._cells = self._square

        if center is not None:
            self.center = center

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
        for x in rng:
            for y in rng:
                yield pos+(x, y)

    def _circle(self, pos):
        sz = self.size - 1
        r = sz/2
        max_dst = r*r+1
        center = pos + Coord(sz, sz) / 2
        for p in self._square(pos):
            if center.dst_sq(p) <= max_dst:
                yield p

    def perimeter(self, circle=None):
        sz = self.size - 1
        if circle is None:
            circle = self.circle

        if not circle:
            yield from (self.pos + (0, i) for i in range(sz))
            yield from (self.pos + (i + 1, 0) for i in range(sz))
            yield from (self.pos + (sz, i + 1) for i in range(sz))
            yield from (self.pos + (i, sz) for i in range(sz))
            return
        else:
            raise NotImplementedError()




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