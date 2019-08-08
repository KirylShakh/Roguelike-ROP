import tcod

from entity_objects.entity import Entity
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.path_functions import path_straight
from render_objects.render_order import RenderOrder

from action_processing.animations.push_animation import PushAnimation


class LightningAnimation:
    def __init__(self, engine, from_point, target, callback_action=None):
        self.engine = engine
        self.from_x, self.from_y = from_point
        self.target = target

        self.path = self.calculate_path()
        self.path_index = 0
        self.completed = False
        self.callback_action = callback_action

        self.lightning_entities = []
        self.lightning_chars = {
            '|': 20,
            '\\': 25,
            '/': 25,
            '~': 15,
            '`': 5,
            str(chr(tcod.CHAR_TEEW)): 5,
            str(chr(tcod.CHAR_TEEE)): 5,
            str(chr(tcod.CHAR_TEEN)): 5,
            str(chr(tcod.CHAR_TEES)): 5,
        }

    def next_tick(self):
        if self.path_index >= len(self.path) or self.completed:
            return []

        x, y = self.path[self.path_index]
        lightning_arc = Entity(x, y, random_choice_from_dict(self.lightning_chars),
                                color_vars.lightning_arc, 'Lightning Arc',
                                render_order=RenderOrder.EFFECT)
        self.lightning_entities.append(lightning_arc)
        self.engine.entities.append(lightning_arc)

        self.path_index += 1
        if self.path_index >= len(self.path):
            return self.complete()

        return []

    def complete(self):
        self.completed = True

        for entity in self.lightning_entities:
            self.engine.entities.remove(entity)

        push_distance = 2
        from_point = (self.from_x, self.from_y)
        animation = PushAnimation(self.engine, self.target, from_point, push_distance)
        self.engine.animations.append(animation)

        if self.callback_action:
            return self.callback_action.run()
        return []

    def calculate_path(self):
        path = path_straight(self.from_x, self.from_y, self.target.x, self.target.y)
        path.append((self.target.x, self.target.y))

        return path
