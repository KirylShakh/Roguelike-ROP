import math
import tcod
from random import randint, choice

from entity_objects.entity import Entity
from render_objects.render_order import RenderOrder
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
            if not dungeon.is_blocked(x, y): # for now there can be many fungi in single tile
                dungeon.tiles[x][y].place_static_entity(self.fungi(x, y))

    def fungi(self, x, y):
        fungi_choices = weight_factor(fungi)
        fungi_choice = random_choice_from_dict(fungi_choices)
        plant_info = fungi[fungi_choice]
        name = 'Luminescent body of {0}'.format(plant_info['name'])

        return Entity(x, y, char=plant_info['char'], color=plant_info['color'],
                    name=name, base_name=plant_info['name'], render_order=RenderOrder.GROUND_FLORA)
