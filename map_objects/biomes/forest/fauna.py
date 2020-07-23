import math
import tcod
from random import randint

from map_objects.biomes.biom_fauna import BiomFauna
from entity_objects.entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from render_objects.render_order import RenderOrder
from random_utils import random_choice_from_dict, from_dungeon_level, weight_factor


monsters = {
    'goblin': {
        'name': 'Goblin',
        'char': 'g',
        'types': {'bandit', 'camper'},
        'attributes': {
            'strength': 7,
            'dexterity': 14,
            'constitution': 8,
            'intelligence': 7,
            'wisdom': 8,
            'charisma': 12,
        },
        'power': 2,
        'defense': 0,
        'xp': 10,
        'color': tcod.desaturated_green,
        'weight_factor': 80,
    },
    'catfolk': {
        'name': 'Catfolk',
        'char': 'c',
        'types': {'bandit', 'camper'},
        'attributes': {
            'strength': 12,
            'dexterity': 16,
            'constitution': 14,
            'intelligence': 9,
            'wisdom': 10,
            'charisma': 13,
        },
        'power': 4,
        'defense': 1,
        'xp': 50,
        'color': tcod.brass,
        'weight_factor': 20,
    },
    'worg': {
        'name': 'Worg',
        'char': 'w',
        'types': {'animal'},
        'attributes': {
            'strength': 16,
            'dexterity': 14,
            'constitution': 11,
            'intelligence': 2,
            'wisdom': 7,
            'charisma': 11,
        },
        'power': 2,
        'defense': 0,
        'xp': 20,
        'color': tcod.gray,
        'weight_factor': 40,
    },
}

class Fauna(BiomFauna):
    def __init__(self):
        self.monsters = monsters

    def populate(self, forest, entities):
        number_of_monsters = round(math.pow(forest.width * forest.height, 0.25))
        monster_chances = weight_factor(monsters)

        for _ in range(number_of_monsters):
            # Choose a random location in room
            x = randint(0, forest.width - 1)
            y = randint(0, forest.height - 1)
            if not forest.is_blocked(x, y) and not entities.find_by_point(x, y):
                monster_choice = random_choice_from_dict(monster_chances)
                monster = self.get_monster(x, y, monster_choice)
                entities.append(monster)
