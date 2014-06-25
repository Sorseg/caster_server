from enum import Enum
from peewee import SqliteDatabase, IntegerField, CharField, ForeignKeyField, CompositeKey, Model
import os

DBNAME = 'caster.db'

if os.path.exists(DBNAME):
    os.remove(DBNAME)

db = SqliteDatabase(DBNAME)


def create_table(cls):
    cls.create_table()
    return cls


class BaseModel(Model):
    class Meta:
        database = db


@create_table
class Location(BaseModel):
    current_turn = IntegerField(default=1)
    name = CharField()


class Object(BaseModel):
    pos_x = IntegerField(null=True)
    pos_y = IntegerField(null=True)


@create_table
class Terrain(Object):

    loc = ForeignKeyField(Location, related_name='terrain')
    terrain_type = IntegerField()

    class Type(Enum):
        wall = 0
        floor = 1
        water = 2
        lava = 3

    class Meta:
        indexes = [(('loc', 'pos_x', 'pos_y'), True)]


@create_table
class Creature(Object):

    loc = ForeignKeyField(Location, null=True, related_name='creatures')
    type = IntegerField()

    class Type(Enum):
        human = 1


class Item(Object):
    owner = ForeignKeyField(Creature, null=True)


@create_table
class Weapon(Item):
    damage = IntegerField()
    loc = ForeignKeyField(Location, null=True, related_name='weapons')
    type = IntegerField()

    class Type(Enum):
        sword = 1
        axe = 2


def populate():
    loc = Location.create(name="Caves")
    sword = Weapon.create(damage=5, type=Weapon.Type.sword)

    return locals()