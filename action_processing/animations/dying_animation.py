from random import randint

from game_vars import color_vars
from game_messages import Message
from render_objects.render_order import RenderOrder
from entity_objects.entity import Entity
from action_processing.animations.basic_animation import BasicAnimation


class DyingAnimation(BasicAnimation):
    def __init__(self, engine, entity):
        super().__init__(engine)
        self.entity = entity
        self.falling_to_tile = self.random_adjancent_tile()

        self.regulatory_flags.add('stumble_phase')

    def next_tick(self):
        if 'stumble_phase' in self.regulatory_flags:
            blood_drop = Entity(self.entity.x, self.entity.y, char=',', color=color_vars.blood,
                                name='Drop of blood', render_order=RenderOrder.TINY_OBJECTS)
            self.engine.world_map.current_dungeon.tiles[self.entity.x][self.entity.y].place_static_entity(blood_drop)

            if self.can_stumble():
                self.entity.x, self.entity.y = self.falling_to_tile
            self.entity.char.set_color(color_vars.blood)

            self.regulatory_flags.discard('stumble_phase')
            self.regulatory_flags.add('fall_phase')
        elif 'fall_phase' in self.regulatory_flags:
            self.entity.char.char = '%'
            self.entity.render_order = RenderOrder.CORPSE
            self.regulatory_flags.discard('fall_phase')
            return [{'message': Message('{0} is dead'.format(self.entity.name.capitalize()), color=color_vars.dead_entity_message)}]
        elif self.regulatory_flags == set():
            self.entity.name = 'remains of {0}'.format(self.entity.name)

            self.engine.entities.remove(self.entity)
            tile = self.engine.world_map.current_dungeon.tiles[self.entity.x][self.entity.y]
            tile.place_static_entity(self.entity)
            self.entity.regulatory_flags.add('moveable')
            tile.set_bg_color(color_vars.blood_pool)
            self.engine.regulatory_flags.add('fov_recompute')

            return self.complete()

        return []

    def random_adjancent_tile(self):
        dx = randint(-1, 1)
        dy = randint(-1, 1)

        return (self.entity.x + dx, self.entity.y + dy)

    def can_stumble(self):
        x, y = self.falling_to_tile
        return not (self.engine.world_map.current_dungeon.is_void(x, y)
                    or self.engine.world_map.current_dungeon.is_blocked(x, y)
                    or self.engine.entities.get_blocking_at_location(x, y))
