from random import randint

from entity_objects.entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from render_objects.render_order import RenderOrder
from random_utils import random_choice_from_dict, weight_factor


class BiomFauna:
    def __init__(self):
        self.monsters = {}

    def get_monster(self, x, y, monster_choice):
        monster = self.monsters[monster_choice]
        fighter_component = Fighter(defense=monster['defense'],
                                power=monster['power'], xp=monster['xp'])
        ai_component = BasicMonster()
        return Entity(x, y, char=monster['char'], color=monster['color'], name=monster['name'], blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component,
                    attributes=monster['attributes'])

    def populate_by_type(self, points, monster_type, entities):
        monster_list = {}
        for name, monster in self.monsters.items():
            if monster_type in monster['types']:
                monster_list[name] = monster

        monster_chances = weight_factor(monster_list)
        for x, y in points:
            monster_choice = random_choice_from_dict(monster_chances)
            monster = self.get_monster(x, y, monster_choice)
            entities.append(monster)
