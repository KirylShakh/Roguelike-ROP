import math
import tcod
from random import randint, choice

from map_objects.char_object import Char
from random_utils import random_choice_from_dict, weight_factor


fungi = {
    'eternal_light_mushroom': {
        'color': tcod.Color(221, 219, 208),
        'name': 'Mycena',
        'char': '.',
        'weight_factor': 4,
    },
    'bitter_oyster': {
        'color': tcod.Color(71, 255, 45),
        'name': 'Panellus',
        'char': ',',
        'weight_factor': 6,
    },
}

class Flora:
    def grow_fungi(self, dungeon, room):
        number_of_fungi = abs(round(math.pow((room.x1 - room.x2) * (room.y1 - room.y2), 0.25)))
        for _ in range(number_of_fungi):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not dungeon.is_blocked(x, y) and not dungeon.tiles[x][y].char:
                dungeon.tiles[x][y].char = self.fungi()

    def fungi(self):
        fungi_choices = weight_factor(fungi)
        fungi_choice = random_choice_from_dict(fungi_choices)
        plant_info = fungi[fungi_choice]

        char = plant_info['char']
        color = plant_info['color']
        name = 'Luminescent body of {0}'.format(plant_info['name'])

        return Plant(char=char, color=color, name=name, base_name=plant_info['name'])

class Plant(Char):
    def __init__(self, char=None, color=None, name=None, base_name=None):
        super(Plant, self).__init__(char=char, color=color, name=name, base_name=base_name)
