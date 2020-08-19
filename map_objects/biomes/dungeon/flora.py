import math
import tcod
from random import randint, choice

from entity_objects.entity import Entity
from map_objects.rectangle import Rect
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

entrance_plants = {
    'wall': {
        'caper bush': {
            'color': tcod.Color(59, 161, 88),
            'flower_color': tcod.Color(240, 240, 240),
            'name': 'Capparis',
            'char': ':',
            'weight_factor': 10,
            'bloom_factor': 3,
        },
        'ivy': {
            'color': tcod.Color(32, 189, 76),
            'flower_color': tcod.Color(147, 201, 30),
            'name': 'Hedera',
            'char': ';',
            'weight_factor': 20,
            'bloom_factor': 7,
        },
        'reindeer lichen': {
            'color': tcod.Color(157, 207, 151),
            'flower_color': tcod.Color(157, 207, 151),
            'name': 'Cladonia',
            'char': '.',
            'weight_factor': 15,
            'bloom_factor': 0,
        },
        'common haircap': {
            'color': tcod.Color(114, 222, 27),
            'flower_color': tcod.Color(114, 222, 27),
            'name': 'Polytrichum',
            'char': ',',
            'weight_factor': 15,
            'bloom_factor': 0,
        },
    },
    'ground': {
        'asarabacca': {
            'color': tcod.Color(67, 156, 91),
            'flower_color': tcod.Color(138, 28, 86),
            'name': 'Asarum',
            'char': '`',
            'weight_factor': 15,
            'bloom_factor': 5,
        },
        'true lovers knot': {
            'color': tcod.Color(83, 145, 80),
            'flower_color': tcod.Color(89, 29, 61),
            'name': 'Paris',
            'char': ',',
            'weight_factor': 10,
            'bloom_factor': 3,
        },
        'wood sorrel': {
            'color': tcod.Color(37, 161, 31),
            'flower_color': tcod.Color(240, 240, 233),
            'name': 'Oxalis',
            'char': '.',
            'weight_factor': 15,
            'bloom_factor': 5,
        },
        'false lily of the valley': {
            'color': tcod.Color(40, 173, 33),
            'flower_color': tcod.Color(240, 240, 240),
            'name': 'Maianthemum',
            'char': ':',
            'weight_factor': 10,
            'bloom_factor': 3,
        },
        'greater celandine': {
            'color': tcod.Color(79, 168, 71),
            'flower_color': tcod.Color(245, 233, 10),
            'name': 'Chelidonium',
            'char': '~',
            'weight_factor': 15,
            'bloom_factor': 5,
        },
    },
}

class Flora:
    def grow_fungi_in_room(self, dungeon, room):
        self.myceliums = []
        self.grow_fungi(dungeon, room, randint(0, 1))

    def grow_cave_twilight_zone(self, cave, twilight_zone):
        self.myceliums = []

        number_of_fungi = abs(round(math.pow(len(twilight_zone), 0.35)))
        for _ in range(number_of_fungi):
            x, y = choice(tuple(twilight_zone))
            if not cave.is_blocked(x, y) and not cave.tiles[x][y].static_entities:
                self.grow_mycelium(x, y, cave)

    def grow_cave_dark_zone(self, cave, dark_zone):
        for x, y in dark_zone:
            if not cave.is_blocked(x, y) and not cave.tiles[x][y].static_entities:
                floor = Entity(x, y, char='~', color=tcod.Color(0, 0, 0), name='Sticky black slime', base_name='Black slime', render_order=RenderOrder.GROUND_FLORA)
                cave.tiles[x][y].place_static_entity(floor)

    def grow_cave_entrance_zone(self, cave, zones):
        wall_plant_choices = weight_factor(entrance_plants['wall'])
        ground_plant_choices = weight_factor(entrance_plants['ground'])

        for entrance_zone in zones:
            center_x, center_y = entrance_zone['center']
            for x, y in entrance_zone['coords']:
                distance_from_center = math.sqrt(pow(center_x - x, 2) + pow(center_y - y, 2))
                chance_for_growth = distance_from_center * 2
                if randint(0, 100) < chance_for_growth:
                    continue

                if cave.is_blocked(x, y):
                    plant_info = entrance_plants['wall'][random_choice_from_dict(wall_plant_choices)]
                else:
                    plant_info = entrance_plants['ground'][random_choice_from_dict(ground_plant_choices)]

                char = plant_info['char']
                base_name = plant_info['name']
                name = base_name
                color = plant_info['color']
                if plant_info.get('bloom_factor'):
                    if randint(1, 100) <= plant_info['bloom_factor']:
                        color = plant_info['flower_color']
                        name = 'blooming {0}'.format(name)

                plant = Entity(x, y, char=char, color=color, name=name, base_name=base_name, render_order=RenderOrder.GROUND_FLORA)
                cave.tiles[x][y].place_static_entity(plant)

    def grow_fungi(self, map_obj, rect, number_of_fungi):
        for _ in range(number_of_fungi):
            x = randint(rect.x1 + 1, rect.x2 - 1)
            y = randint(rect.y1 + 1, rect.y2 - 1)
            if not map_obj.is_blocked(x, y) and not map_obj.tiles[x][y].static_entities:
                self.grow_mycelium(x, y, map_obj)

    def grow_mycelium(self, center_x, center_y, map_obj):
        fungi_choices = weight_factor(fungi)
        fungi_choice = random_choice_from_dict(fungi_choices)
        plant_info = fungi[fungi_choice]

        self.myceliums.append({
            'center': (center_x, center_y),
            'plant': fungi_choice,
        })

        mycelium_radius = randint(0, 5)
        for distance in range(mycelium_radius):
            chance_for_fungi = distance * 20
            for dx in range(-distance, distance):
                dy = int(pow(distance * distance - dx * dx, 0.5))
                dys = [-dy, dy]
                for dy in dys:
                    if randint(0, 100) < chance_for_fungi:
                        continue
                    x = center_x + dx
                    y = center_y + dy
                    if not map_obj.is_void(x, y) and not map_obj.tiles[x][y].static_entities:
                        map_obj.tiles[x][y].place_static_entity(self.fungi(x, y, plant_info))

    def fungi(self, x, y, plant_info):
        name = 'Luminescent body of {0}'.format(plant_info['name'])

        return Entity(x, y, char=plant_info['char'], color=plant_info['color'],
                    name=name, base_name=plant_info['name'], render_order=RenderOrder.GROUND_FLORA)
