import collections
from enum import Enum
from peewee import SqliteDatabase, IntegerField, CharField, ForeignKeyField, CompositeKey, Model

#Temporary terrain container:
from PIL import Image
from geometry import Coord
import geometry

map_data = Image.open('maps/start.png').load()
Pixel = collections.namedtuple('Pixel', 'r g b ttype')

SIGHT = 8

DBNAME = 'caster.db'

db = SqliteDatabase(DBNAME)
tables_to_create = []


def create_table(cls):
    tables_to_create.append(cls)
    return cls


def init():
    for t in tables_to_create:
        t.create_table()


class BaseModel(Model):
    class Meta:
        database = db


class Object(BaseModel):
    pos_x = IntegerField(null=True)
    pos_y = IntegerField(null=True)

    @property
    def pos(self):
        return Coord(self.pos_x, self.pos_y)

    @pos.setter
    def pos(self, val):
        self.pos_x, self.pos_y = val

@create_table
class Terrain(Object):

    terrain_type = IntegerField()

    class Type(Enum):
        wall = 0
        floor = 1
        water = 2
        lava = 3

    class Meta:
        indexes = [(('pos_x', 'pos_y'), True)]


@create_table
class Creature(Object):

    type = IntegerField()
    user = CharField(unique=True)
    name = CharField(unique=True)
    max_hp = IntegerField()
    hp = IntegerField()
    sight = SIGHT

    class Type(Enum):
        human = 1

    def dict(self):
        return dict(
            what="creature",
            coords=self.pos,
            name=self.name,
            sight=self.sight,
            hp=self.hp,
            max_hp=self.max_hp
        )


class Item(Object):
    owner = ForeignKeyField(Creature, null=True)


@create_table
class Weapon(Item):
    damage = IntegerField()
    type = IntegerField()

    class Type(Enum):
        sword = 1
        axe = 2


def get_creature(login, password) -> Creature:
    c = Creature.select().where(Creature.user == login)
    if c.count() < 1:
        return
    return c.get()


def get_pixel(coord: tuple)->Pixel:
    pixel = list(map_data[coord[0], coord[1]])
    pixel.append('wall' if all(c < 200 for c in pixel) else 'floor')
    return Pixel(*pixel)


def get_environment(creature: Creature):

    a = geometry.Area(SIGHT*2+1, center=creature.pos, circle=True)
    res = {}
    for cell in a.cells():
        p = get_pixel(cell)
        res["{},{}".format(*cell)] = list(p)

    return res