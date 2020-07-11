import tcod
from random import randint, choice

from entity_objects.static_entity import StaticEntity
from render_objects.render_order import RenderOrder
from random_utils import random_choice_from_dict, weight_factor


trees = {
    'elm': {
        'color': tcod.Color(40, 28, 4),
        'name': 'Ulmus',
        'weight_factor': 50,
    },
    'sequoia': {
        'color': tcod.Color(80, 50, 5),
        'name': 'Sequoia',
        'weight_factor': 40,
    },
    'birch': {
        'color': tcod.Color(147, 137, 128),
        'name': 'Betula',
        'weight_factor': 20,
    },
    'alder': {
        'color': tcod.Color(100, 100, 100),
        'name': 'Alnus',
        'weight_factor': 15,
    },
    'acacia': {
        'color': tcod.Color(79, 78, 68),
        'name': 'Acacia',
        'weight_factor': 5,
    },
    'willow': {
        'color': tcod.Color(71, 28, 7),
        'name': 'Salix',
        'weight_factor': 5,
    },
    'bird_cherry': {
        'color': tcod.Color(64, 58, 40),
        'name': 'Prunus',
        'weight_factor': 5,
    },
    'lemon': {
        'color': tcod.Color(64, 89, 20),
        'name': 'Citrus',
        'weight_factor': 5,
    },
}

tree_choices = weight_factor(trees)

one_tile_plants = {
    # angiosperms
    'aposeris': {
        'color': tcod.Color(87, 237, 80),
        'flower_color': tcod.Color(238, 238, 88),
        'name': 'Aposeris',
        'lifeform': 'Sprout',
        'char': ';',
        'weight_factor': 40,
        'bloom_factor': 5,
    },
    'astrancia': {
        'color': tcod.Color(27, 176, 19),
        'flower_color': tcod.Color(215, 29, 2),
        'name': 'Astrancia',
        'lifeform': 'Sprout',
        'char': ',',
        'weight_factor': 35,
        'bloom_factor': 10,
    },
    'astilboides': {
        'color': tcod.Color(31, 202, 21),
        'flower_color': tcod.Color(238, 130, 238),
        'name': 'Astilboides',
        'lifeform': 'Sprout',
        'char': ';',
        'weight_factor': 25,
        'bloom_factor': 5,
    },
    'hellebore': {
        'color': tcod.Color(27, 176, 19),
        'flower_color': tcod.Color(219, 89, 92),
        'name': 'Helleborus',
        'lifeform': 'Sprout',
        'char': ':',
        'weight_factor': 20,
        'bloom_factor': 5,
    },
    'tricyrtis': {
        'color': tcod.Color(101, 219, 98),
        'flower_color': tcod.Color(245, 245, 245),
        'name': 'Tricyrtis',
        'lifeform': 'Sprout',
        'char': '\'',
        'weight_factor': 35,
        'bloom_factor': 5,
    },
    'blueberry': {
        'color': tcod.Color(27, 176, 19),
        'flower_color': tcod.Color(240, 242, 174),
        'name': 'Vaccinium',
        'lifeform': 'Shrub',
        'char': '"',
        'weight_factor': 30,
        'bloom_factor': 10,
    },
    'bergenia': {
        'color': tcod.Color(31, 202, 21),
        'flower_color': tcod.Color(240, 125, 188),
        'name': 'Bergenia',
        'lifeform': 'Sprout',
        'char': '`',
        'weight_factor': 35,
        'bloom_factor': 5,
    },
    # gymnosperms
    'juniper': {
        'color': tcod.Color(27, 176, 19),
        'name': 'Juniperus',
        'lifeform': 'Shrub',
        'char': '~',
        'weight_factor': 35,
    },
}

fungi = {
    'fly_agaric': {
        'color': tcod.Color(230, 40, 45),
        'name': 'Amanita',
        'char': '.',
        'weight_factor': 15,
    },
    'boletus': {
        'color': tcod.Color(214, 183, 52),
        'name': 'Boletus',
        'char': '.',
        'weight_factor': 3,
    },
}

saplings = {
    'Y': 15,
    'T': 10,
    '|': 10,
    '\\': 7,
    '/': 7,
}

soil = {' ': 5}

saplings_colors = [
    tcod.Color(101, 219, 98),
    tcod.Color(87, 237, 80),
    tcod.Color(31, 202, 21),
    tcod.Color(27, 176, 19),
]

one_tile_plant_choices = weight_factor(one_tile_plants)

class Flora:
    def __init__(self, average_tree_diameter):
        self.average_tree_diameter = average_tree_diameter

        self.primary = random_choice_from_dict(tree_choices)
        self.secondary = random_choice_from_dict(tree_choices)

        self.tree_choices = {}
        self.tree_choices[self.primary] = 90
        self.tree_choices[self.secondary] = 10

    def get_tree(self):
        diameter = randint(1, self.average_tree_diameter * 2)
        tree_key = random_choice_from_dict(self.tree_choices)

        base_name = base_name=trees[tree_key]['name']
        if diameter < 4:
            name = 'Trunk of {0}'.format(base_name)
        else:
            name = 'Giant trunk of {0}'.format(base_name)

        return Tree(bg_color=trees[tree_key]['color'], name=name, base_name=base_name, diameter=diameter)

    def get_tile_plant(self, x, y, tile_shadowed):
        plant_choice = self.choose_plant(tile_shadowed)

        if one_tile_plants.get(plant_choice):
            return self.grass_plant(x, y, plant_choice, tile_shadowed)
        elif fungi.get(plant_choice):
            return self.fungi(x, y, plant_choice)
        else:
            return self.sapling(x, y, plant_choice, tile_shadowed)

    def choose_plant(self, tile_shadowed):
        plant_choices = one_tile_plant_choices.copy()
        if tile_shadowed:
            plant_choices.update(weight_factor(fungi))
            plant_choices.update({k: (v // 3) for k, v in saplings.items()})
            plant_choices.update({k: (v * 2) for k, v in soil.items()})
        else:
            plant_choices.update(saplings)
            plant_choices.update(soil)

        return random_choice_from_dict(plant_choices)

    def grass_plant(self, x, y, plant_choice, tile_shadowed):
        plant_info = one_tile_plants[plant_choice]

        char = plant_info['char']
        base_name = plant_info['name']
        name = base_name

        color = plant_info['color']
        if plant_info.get('bloom_factor'):
            if randint(1, 100) <= plant_info['bloom_factor']:
                color = plant_info['flower_color']
                name = 'blooming {0}'.format(name)

        name = '{0} of {1}'.format(plant_info['lifeform'], name)
        if not tile_shadowed:
            name += ' on a sunny glade'

        return StaticEntity(x, y, char=char, color=color, name=name, base_name=base_name, render_order=RenderOrder.GROUND_FLORA)

    def fungi(self, x, y, plant_choice):
        plant_info = fungi[plant_choice]

        char = plant_info['char']
        color = plant_info['color']
        name = 'Fruiting body of {0}'.format(plant_info['name'])

        return StaticEntity(x, y, char=char, color=color, name=name, base_name=plant_info['name'],
                            render_order=RenderOrder.GROUND_FLORA)

    def sapling(self, x, y, char, tile_shadowed):
        color = choice(saplings_colors)
        base_name, name = self.sapling_name(char)

        if not tile_shadowed:
            name += ' on a sunny glade'

        return StaticEntity(x, y, char=char, color=color, name=name, base_name=base_name, render_order=RenderOrder.GROUND_FLORA)

    def sapling_name(self, sapling):
        primary_tree = trees[self.primary]['name']
        secondary_tree = trees[self.secondary]['name']
        names = {
            'Y': (primary_tree, 'Sapling of {0}'.format(primary_tree)),
            'T': (secondary_tree, 'Sapling of {0}'.format(secondary_tree)),
            '|': (primary_tree, 'Withered sapling of {0}'.format(primary_tree)),
            '\\': (primary_tree, 'Withered sapling of {0}'.format(primary_tree)),
            '/': (secondary_tree, 'Withered sapling of {0}'.format(secondary_tree)),
            ' ': ('Soil', 'Patch of soil'),
        }

        return names[sapling]

class Tree(StaticEntity):
    def __init__(self, char=None, color=None, bg_color=None, name=None, base_name=None, diameter=1):
        super().__init__(-1, -1, char=char, color=color, bg_color=bg_color, name=name, base_name=base_name,
                            blocks=True, render_order=RenderOrder.GROUND_FLORA)

        self.diameter = diameter

    def set_trunk(self, trunk):
        self.trunk = trunk
