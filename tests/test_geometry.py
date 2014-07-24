import unittest
import geometry


def put(c):
    print(c, end='')


def draw(cells):
    screen = [['.' for x in range(20)] for y in range(20)]
    #cells = a.cells()

    for c in cells:
        if screen[c.y][c.x] == '#':
            screen[c.y][c.x] = '!'
        else:
            screen[c.y][c.x] = '#'

    for y in screen:
        print(*y, sep='')

    '''
    for y in range(20):
        for x in range(20):
            char = '.'
            if (x, y) in cells:
                char = '#'
            if (x, y) == a.pos:
                char = {'.': '?', '#': '@'}[char]

            put(char)
        print()
    '''


class TestGeometry(unittest.TestCase):

    def test_coords(self):
        c = geometry.Coord(11, 12)
        self.assertEqual(c.x, 11)
        self.assertEqual(c.y, 12)
        self.assertEqual(c+(2, 1), (13, 13))

    def test_area_center(self):
        c = geometry.Area(6)
        c.center = (3, 3)
        self.assertEqual(c.pos, (0, 0))

    def test_coord_div(self):
        c = geometry.Coord(6, 6)
        self.assertEqual(c/2, (3, 3))

    def test_overlap(self):
        A = geometry.Area
        c1 = A(5, (1, 1))
        c2 = A(5, (2, 2))
        self.assertTrue(c1 & c2)
        c1 = A(5)
        c2 = A(5, (15, 15))
        self.assertFalse(c1 & c2)

    def test_area(self):
        for i in range(10):
            a = geometry.Area(i, (5, 5)).cells()
            self.assertEqual(len(list(a)), i*i)

    def test_circle(self):
        for i in range(5, 20):
            a = geometry.Area(i, (0, 0), circle=True)
            print(i)
            draw(a.cells())

    def test_line(self):
        l1 = geometry.Line((4, 3))
        self.assertEqual(list(l1.cells()), [
            (0, 0),
            (1, 0),
            (2, 1),
            (3, 2),
            (4, 3)
        ])
        l2 = geometry.Line((3, 4))
        self.assertEqual(list(l2.cells()), [
            (0, 0),
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4)
        ])
        l = geometry.Line((2, 2), (4, 5))
        self.assertEqual(list(l.cells()), [
            (2, 2),
            (2, 3),
            (3, 4),
            (4, 5)
        ])
        self.assertEqual(list(l.cells()),
                         list(geometry.Line((2, 3)).cells((2, 2))))

    def test_perimeter(self):
        a = geometry.Area(5, (4, 4))
        #draw(a.perimeter())
        #draw(a.cells())
        self.assertTrue(set(a.cells()) >= set(a.perimeter()))

