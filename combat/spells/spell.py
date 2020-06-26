from random import randint
from enum import Enum, auto


class SpellTags(Enum):
    DAMAGE = auto()
    HEAL = auto()
    MIND = auto()
    ELEMENTAL = auto()
    FIRE = auto()
    ELECTRICITY = auto()


class Spell:
    def __init__(self, caster_level):
        self.caster_level = caster_level
        self.tags = []

        self.setup()

    def setup(self):
        self.level = 0
        self.value_die = 1

    @property
    def tire_cost(self):
        return self.level

    def inflicted_value(self):
        return sum([randint(1, self.value_die) for _ in range(self.caster_level)])

    @property
    def resist_by(self):
        return None

    def apply_status(self, target):
        return []

    def harm_message(self, target):
        return ''
