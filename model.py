from enum import Enum
import json
from peewee import SqliteDatabase, IntegerField, CharField, ForeignKeyField, CompositeKey, Model
import os

#Temporary terrain container:
from PIL import Image
from geometry import TerrainPiece

map_data = Image.open('maps/start.png').load()


SIGHT = 5

DBNAME = 'caster.db'

db = SqliteDatabase(DBNAME)
tables_to_create = []


def create_table(cls):
    tables_to_create.append(cls)
    return cls


def init():
    if not os.path.exists(DBNAME):
        for t in tables_to_create:
            t.create_table()


class BaseModel(Model):
    class Meta:
        database = db


class Object(BaseModel):
    pos_x = IntegerField(null=True)
    pos_y = IntegerField(null=True)


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

    class Type(Enum):
        human = 1

    def dict(self):
        return dict(
            what="creature",
            coords=[self.pos_x, self.pos_y],
            name=self.name
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
    return Creature.get(Creature.user == login)


def get_environment(creature):
    return TerrainPiece(
        (creature.pos_x, creature.pos_y),
        SIGHT,
        map_data).dict()