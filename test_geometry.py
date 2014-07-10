import unittest
import geometry


def put(c):
    print(c, end='')


def draw(cells):
    for y in range(20):
        for x in range(20):
            char = '.'
            if (x, y) in cells:
                char = '#'
            if (x, y) == (5, 5):
                char = {'.': '?', '#': '@'}[char]

            put(char)
        print()


class TestGeometry(unittest.TestCase):

    def test_coords(self):
        c = geometry.Coord(11, 12)
        self.assertEqual(c.x, 11)
        self.assertEqual(c.y, 12)
        self.assertEqual(c+(2, 1), (13, 13))

    def test_coord_div(self):
        c = geometry.Coord(6, 6)
        self.assertEqual(c/2, (3, 3))

    def test_area(self):
        for i in range(10):
            a = geometry.Area((5, 5), i).cells()
            self.assertEqual(len(a), i*i)
