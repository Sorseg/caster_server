import json

circle_approx = [
                  (),

                  ('#'),

                  ('##',
                   '##'),

                  ('###',
                   '###',
                   '###'),

                  (' ## ',
                   '####',
                   '####',
                   ' ## '),

                  (' ### ',
                   '#####',
                   '#####',
                   '#####',
                   ' ### ')
                ]


# list of coordinate approximations for large objects
approx_maps = [
              {(x,y) for y, line in enumerate(approx)
                     for x, c in enumerate(line) if c =='#'}
              for approx in circle_approx
              ]


class Coord(tuple):

    def __add__(self, c):
        return Coord([i + j for i, j in zip(self, c)])

    def __str__(self):
        return "{},{}".format(*self)

    def dist(c1, c2):
        x1, y1 = c1
        x2, y2 = c2
        return ((x2-x1)**2 + (y2-y1)**2)**0.5


class Area(object):
    """Piece of space"""

    def __init__(self, coord, size):
        self.coord = coord
        self.size = size

    def fits(self, new_pos, location):

        floor = {coordinate for coordinate, cell in location.cells.items() if cell.type != 'wall' }
        occupied = set()
        if location.creatures:
            occupied.update(*[cr.space().cells() for cr in location.creatures])
        new_cells = self.cells(new_pos)
        return (new_cells <= floor) and not (new_cells & occupied)

    def cells(self, pos = None):
        if not pos:
            pos = self.coord
        return {Coord(pos)+c for c in approx_maps[self.size]}


class TerrainPiece:
    def __init__(self, pos, size, map_data):
        pos_x, pos_y = map(int, pos)
        self.terrain_dict = {}
        for x in range(pos_x - size, pos_x + size+1):
            for y in range(pos_y - size, pos_y + size+1):
                pixel = list(map_data[(x, y)])
                ttype = 'wall' if all(c < 200 for c in pixel) else 'floor'
                pixel.append(ttype)
                self.terrain_dict[(x, y)] = pixel

    def dict(self):
        return {"{},{}".format(*k):p for k,p in self.terrain_dict.items()}