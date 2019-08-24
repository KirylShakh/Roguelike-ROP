import tcod
from random import randint

from entity_objects.entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from render_objects.render_order import RenderOrder
from random_utils import random_choice_from_dict, from_dungeon_level, weight_factor


# [max_number, dungeon_level]
max_monsters_per_room_weights = [[2, 1], [3, 4], [5, 6]]

monsters = {
    'orc': {
        'name': 'Orc',
        'char': 'o',
        'hp': 20,
        'power': 4,
        'defense': 0,
        'xp': 35,
        'color': tcod.desaturated_green,
        'weight_factor': 80,
    },
    'troll': {
        'name': 'Troll',
        'char': 'T',
        'hp': 30,
        'power': 8,
        'defense': 2,
        'xp': 100,
        'color': tcod.darker_green,
        'weight_factor': [[15, 3], [30, 5], [60, 7]],
    },
}

class Fauna:
    def populate_room(self, room, dungeon_level, entities):
        max_monsters_per_room = from_dungeon_level(max_monsters_per_room_weights, dungeon_level)
        number_of_monsters = randint(0, max_monsters_per_room)
        monster_chances = weight_factor(monsters, dungeon_level)

        for _ in range(number_of_monsters):
            # Choose a random location in room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not entities.find_by_point(x, y):
                monster_choice = random_choice_from_dict(monster_chances)
                monster = self.get_monster(x, y, monster_choice)
                entities.append(monster)

    def get_monster(self, x, y, monster_choice):
        monster = monsters[monster_choice]
        fighter_component = Fighter(hp=monster['hp'], defense=monster['defense'],
                                power=monster['power'], xp=monster['xp'])
        ai_component = BasicMonster()
        return Entity(x, y, monster['char'], monster['color'], monster['name'], blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
