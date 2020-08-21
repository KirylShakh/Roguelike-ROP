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
        'display_name': 'Luminescent body of Mycena',
        'char': '.',
        'weight_factor': 4,
    },
    'bitter_oyster': {
        'color': tcod.Color(71, 255, 45),
        'name': 'Panellus',
        'display_name': 'Luminescent body of Panellus',
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
            'display_name': 'Wall overgrown with Capparis',
            'char': ':',
            'weight_factor': 10,
            'bloom_factor': 3,
        },
        'ivy': {
            'color': tcod.Color(32, 189, 76),
            'flower_color': tcod.Color(147, 201, 30),
            'name': 'Hedera',
            'display_name': 'Wall overgrown with Hedera',
            'char': ';',
            'weight_factor': 20,
            'bloom_factor': 7,
        },
        'reindeer lichen': {
            'color': tcod.Color(157, 207, 151),
            'flower_color': tcod.Color(157, 207, 151),
            'name': 'Cladonia',
            'display_name': 'Wall overgrown with Cladonia',
            'char': '.',
            'weight_factor': 15,
            'bloom_factor': 0,
        },
        'common haircap': {
            'color': tcod.Color(114, 222, 27),
            'flower_color': tcod.Color(114, 222, 27),
            'name': 'Polytrichum',
            'display_name': 'Wall overgrown with Polytrichum',
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
            'display_name': 'Sprout of Asarum',
            'char': '`',
            'weight_factor': 15,
            'bloom_factor': 5,
        },
        'true lovers knot': {
            'color': tcod.Color(83, 145, 80),
            'flower_color': tcod.Color(89, 29, 61),
            'name': 'Paris',
            'display_name': 'Sprout of Paris',
            'char': ',',
            'weight_factor': 10,
            'bloom_factor': 3,
        },
        'wood sorrel': {
            'color': tcod.Color(37, 161, 31),
            'flower_color': tcod.Color(240, 240, 233),
            'name': 'Oxalis',
            'display_name': 'Sprout of Oxalis',
            'char': '.',
            'weight_factor': 15,
            'bloom_factor': 5,
        },
        'false lily of the valley': {
            'color': tcod.Color(40, 173, 33),
            'flower_color': tcod.Color(240, 240, 240),
            'name': 'Maianthemum',
            'display_name': 'Sprout of Maianthemum',
            'char': ':',
            'weight_factor': 10,
            'bloom_factor': 3,
        },
        'greater celandine': {
            'color': tcod.Color(79, 168, 71),
            'flower_color': tcod.Color(245, 233, 10),
            'name': 'Chelidonium',
            'display_name': 'Sprout of Chelidonium',
            'char': '~',
            'weight_factor': 15,
            'bloom_factor': 5,
        },
    },
}

deep_cave_flora = {
    'earth sap': {
        'color': tcod.Color(0, 0, 0),
        'name': 'Black Earth Sap',
        'display_name': 'Warm to the touch pitch black sap',
        'max_thicket_radius': 10,
        'char': '~',
        'weight_factor': 25,
    },
    'magma fungus': {
        'color': [tcod.Color(204, 67, 29), tcod.Color(242, 238, 10), tcod.Color(227, 166, 45)],
        'name': 'Magma Fungus',
        'display_name': 'Shimmering body of Magma Fungus',
        'max_thicket_radius': 4,
        'char': '"',
        'weight_factor': 10,
    },
    'singer crystals': {
        'color': [tcod.Color(153, 7, 237), tcod.Color(158, 240, 227), tcod.Color(71, 148, 255), tcod.Color(232, 56, 203), tcod.Color(254, 255, 128)],
        'name': 'Singer Crystal',
        'display_name': 'Glowing with multitudes of colors silently ringing crystal',
        'max_thicket_radius': 2,
        'char': '^',
        'weight_factor': 5,
    },
}

class Flora:
    def grow_fungi_in_room(self, dungeon, room):
        self.thickets = []
        self.grow_fungi(dungeon, room, randint(0, 1))

    def grow_cave_twilight_zone(self, cave, twilight_zone):
        self.thickets = []

        number_of_fungi = abs(round(math.pow(len(twilight_zone), 0.35)))
        for _ in range(number_of_fungi):
            x, y = choice(tuple(twilight_zone))
            if not cave.is_blocked(x, y) and not cave.tiles[x][y].static_entities:
                self.grow_thicket(x, y, cave)

    def grow_cave_dark_zone(self, cave, dark_zone):
        number_of_flora = min(abs(round(math.pow(len(dark_zone), 0.25))) * cave.dungeon_level, 200)
        for _ in range(number_of_flora):
            x, y = choice(tuple(dark_zone))
            if not cave.is_blocked(x, y) and not cave.tiles[x][y].static_entities:
                self.grow_thicket(x, y, cave, flora_data=deep_cave_flora)

    def grow_cave_entrance_zone(self, cave, zones):
        wall_plant_choices = weight_factor(entrance_plants['wall'])
        ground_plant_choices = weight_factor(entrance_plants['ground'])

        for entrance_zone in zones:
            center_x, center_y = entrance_zone['center']
            for x, y in entrance_zone['coords']:
                if cave.tiles[x][y].static_entities:
                    continue

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
                name = plant_info['display_name']
                color = plant_info['color']
                if type(color) == list:
                    color = choice(color)
                if plant_info.get('bloom_factor'):
                    if randint(1, 100) <= plant_info['bloom_factor']:
                        color = plant_info['flower_color']
                        name = 'Blooming {0}'.format(name)

                plant = Entity(x, y, char=char, color=color, name=name, base_name=base_name, render_order=RenderOrder.GROUND_FLORA)
                cave.tiles[x][y].place_static_entity(plant)

    def grow_fungi(self, map_obj, rect, number_of_fungi):
        for _ in range(number_of_fungi):
            x = randint(rect.x1 + 1, rect.x2 - 1)
            y = randint(rect.y1 + 1, rect.y2 - 1)
            if not map_obj.is_blocked(x, y) and not map_obj.tiles[x][y].static_entities:
                self.grow_thicket(x, y, map_obj)

    def grow_thicket(self, center_x, center_y, map_obj, flora_data=fungi):
        flora_choices = weight_factor(flora_data)
        flora_choice = random_choice_from_dict(flora_choices)
        plant_info = flora_data[flora_choice]

        self.thickets.append({
            'center': (center_x, center_y),
            'plant': flora_choice,
        })

        min_radius = flora_data.get('min_thicket_radius', 0)
        max_radius = flora_data.get('max_thicket_radius', 5)
        thicket_radius = randint(min_radius, max_radius)
        for distance in range(thicket_radius):
            chance_for_plant = distance * 20
            for dx in range(-distance, distance):
                dy = int(pow(distance * distance - dx * dx, 0.5))
                dys = [-dy, dy]
                for dy in dys:
                    if randint(0, 100) < chance_for_plant:
                        continue
                    x = center_x + dx
                    y = center_y + dy
                    if not map_obj.is_void(x, y) and not map_obj.tiles[x][y].static_entities:
                        map_obj.tiles[x][y].place_static_entity(self.plant(x, y, plant_info))

    def plant(self, x, y, plant_info):
        color = plant_info['color']
        if type(color) == list:
            color = choice(color)

        return Entity(x, y, char=plant_info['char'], color=color,
                    name=plant_info['display_name'], base_name=plant_info['name'], render_order=RenderOrder.GROUND_FLORA)
