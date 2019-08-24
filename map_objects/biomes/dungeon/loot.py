import tcod
from random import randint

from entity_objects.entity import Entity
from components.equippable import Equippable
from components.equipment import EquipmentSlots
from components.item import Item
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from render_objects.render_order import RenderOrder
from game_messages import Message
from map_objects.char_object import Char
from random_utils import random_choice_from_dict, from_dungeon_level, weight_factor
from game_vars import color_vars, message_vars


# [max_number, dungeon_level]
max_items_per_room_weights = [[1, 1], [2, 4]]

items = {
    'healing_potion': {
        'name': 'Healing potion',
        'char': '!',
        'color': tcod.violet,
        'weight_factor': 35,
        'item_component': {
            'use_function': heal,
            'amount': 40,
        },
    },
    'dagger': {
        'name': 'Dagger',
        'char': '-',
        'color': tcod.sky,
        'weight_factor': 0,
        'equippable_component': {
            'slot': EquipmentSlots.MAIN_HAND,
            'power_bonus': 2,
        },
    },
    'sword': {
        'name': 'Sword',
        'char': '/',
        'color': tcod.sky,
        'weight_factor': [[5, 4]],
        'equippable_component': {
            'slot': EquipmentSlots.MAIN_HAND,
            'power_bonus': 3,
        },
    },
    'shield': {
        'name': 'Shield',
        'char': ']',
        'color': tcod.darker_orange,
        'weight_factor': [[15, 8]],
        'equippable_component': {
            'slot': EquipmentSlots.OFF_HAND,
            'defense_bonus': 1,
        },
    },
    'confuse_scroll': {
        'name': 'Confuse Scroll',
        'char': '#',
        'color': tcod.light_pink,
        'weight_factor': [[10, 2]],
        'item_component': {
            'use_function': cast_confuse,
            'targeting': True,
            'targeting_message': Message(message_vars.confuse_target_message, color_vars.target_message),
        },
    },
    'lightning_scroll': {
        'name': 'Lightning Scroll',
        'char': '#',
        'color': tcod.yellow,
        'weight_factor': [[25, 4]],
        'item_component': {
            'use_function': cast_lightning,
            'damage': 40,
            'maximum_range': 5,
        },
    },
    'fireball_scroll': {
        'name': 'Fireball Scroll',
        'char': '#',
        'color': tcod.red,
        'weight_factor': [[25, 6]],
        'item_component': {
            'use_function': cast_fireball,
            'targeting': True,
            'targeting_message': Message(message_vars.fireball_target_message, color_vars.target_message),
            'damage': 25,
            'radius': 3,
        },
    },
}

class Loot:
    def fill_room(self, room, dungeon_level, entities):
        max_items_per_room = from_dungeon_level(max_items_per_room_weights, dungeon_level)
        number_of_items = randint(0, max_items_per_room)
        item_chances = weight_factor(items, dungeon_level)

        for _ in range(number_of_items):
            # Choose a random location in room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not entities.find_by_point(x, y):
                item_choice = random_choice_from_dict(item_chances)
                item = self.get_item(x, y, item_choice)
                entities.append(item)

    def get_item(self, x, y, item_choice):
        item = items[item_choice]

        item_component = None
        equippable_component = None

        if item.get('item_component'):
            item_component = Item(**item['item_component'])
        if item.get('equippable_component'):
            equippable_component = Equippable(**item['equippable_component'])

        return Entity(x, y, item['char'], item['color'], item['name'],
                    render_order=RenderOrder.ITEM, item=item_component, equippable=equippable_component)
