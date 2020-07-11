from random import randint, choice

from entity_objects.entity import Entity
from entity_objects.static_entity import StaticEntity
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.path_functions import path_straight
from render_objects.render_order import RenderOrder
from map_objects.rectangle import Rect

from action_processing.animations.basic_animation import BasicAnimation


class ChoppedBodyPartAnimation(BasicAnimation):
    def __init__(self, engine, body_part_owner, body_part_name='Limb'):
        super().__init__(engine)

        self.blood_chars = {
            '.': 25,
            ',': 15,
            '~': 20,
            '`': 15,
        }
        self.default_body_part_char = '-'
        self.body_part_spinning_chars = ['/', '-', '\\', '|']
        self.spinning_index = 0
        self.spinning_chars_len = len(self.body_part_spinning_chars)

        self.body_part_owner = body_part_owner
        self.calculate_path()

        x, y = self.path[0]
        if self.engine.world_map.current_dungeon.is_void(x, y) or self.engine.world_map.current_dungeon.is_blocked(x, y):
            x = self.body_part_owner.x
            y = self.body_part_owner.y
        self.body_part = Entity(x, y, char=self.default_body_part_char, color=color_vars.body,
                                name=body_part_name, render_order=RenderOrder.EFFECT)
        self.engine.entities.append(self.body_part)

        self.animation_entities = []
        self.trail_length = 3

    def next_tick(self):
        if self.path_index >= len(self.path) or self.completed:
            return self.stop()

        self.body_part.char.char = self.body_part_spinning_chars[self.spinning_index]

        self.spinning_index += 1
        if self.spinning_index == self.spinning_chars_len:
            self.spinning_index = 0

        if self.stop_condition():
            # path became blocked. for now simply stopping moving
            return self.stop()
        elif 'path_index_changed' in self.regulatory_flags:
            self.handle_blood_path()

            x, y = self.path[self.path_index]
            self.body_part.x = x
            self.body_part.y = y
            self.engine.regulatory_flags.add('fov_recompute')

        if self.spinning_index % 2 == 0:
            self.path_index += 1
            self.regulatory_flags.add('path_index_changed')
        else:
            self.regulatory_flags.discard('path_index_changed')

        if self.path_index == len(self.path):
            return self.complete()

        return []

    def complete(self):
        self.completed = True
        self.body_part.render_order = RenderOrder.SMALL_OBJECTS
        self.body_part.char.char = self.default_body_part_char

        self.body_part.char.bg_color = color_vars.blood_pool
        self.body_part.char.regulatory_flags.add('bg_color_stacks')
        self.engine.entities.remove(self.body_part)
        tile = self.engine.world_map.current_dungeon.tiles[self.body_part.x][self.body_part.y]
        tile.place_static_entity(self.body_part)
        self.engine.regulatory_flags.add('fov_recompute')

        for blood_drop in self.animation_entities:
            blood_drop.render_order = RenderOrder.TINY_OBJECTS
        return []

    def stop_condition(self):
        x, y = self.path[self.path_index]
        return (self.engine.world_map.current_dungeon.is_void(x, y)
                    or self.engine.world_map.current_dungeon.is_blocked(x, y)
                    or self.engine.entities.get_blocking_at_location(x, y))

    def handle_blood_path(self):
        blood_char = random_choice_from_dict(self.blood_chars)
        blood_entity = StaticEntity(self.body_part.x, self.body_part.y,
                                char=blood_char, color=color_vars.blood,
                                name='Drop of blood', render_order=RenderOrder.EFFECT)
        self.engine.world_map.current_dungeon.tiles[self.body_part.x][self.body_part.y].place_static_entity(blood_entity)
        self.animation_entities.append(blood_entity)
        if len(self.animation_entities) > self.trail_length:
            entity_to_remove = self.animation_entities.pop(0)
            tile = self.engine.world_map.current_dungeon.tiles[entity_to_remove.x][entity_to_remove.y]
            tile.remove_static_entity(entity_to_remove)

    def calculate_path(self):
        min_distance, max_distance = (2, 5)
        distance = randint(min_distance, max_distance)

        end_x, end_y = self.end_point(distance)

        start_x = self.body_part_owner.x
        start_y = self.body_part_owner.y

        self.path = path_straight(start_x, start_y, end_x, end_y, distance)
        self.path.append((end_x, end_y))
        self.path_index = 0

    def end_point(self, distance):
        x = max(self.body_part_owner.x - distance, 0)
        y = max(self.body_part_owner.y - distance, 0)
        side = 2 * distance

        return choice(Rect(x, y, side, side).calculate_border_tiles())
