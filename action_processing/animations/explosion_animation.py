import tcod

from action_processing.animations.push_animation import PushAnimation
from entity_objects.entity import Entity
from render_objects.render_order import RenderOrder
from game_messages import Message
from game_vars import color_vars


class ExplosionAnimation:
    def __init__(self, engine, from_point, radius, color, damage, callback_action=None):
        self.engine = engine
        self.from_x, self.from_y = from_point
        self.radius = radius
        self.damage = damage
        self.color = color
        self.char = tcod.CHAR_BLOCK1

        self.path_index = 0
        self.completed = False

        self.explosion_entities = []

    def next_tick(self):
        results = []

        if self.path_index == 0:
            self.add_explosion_entity(self.from_x, self.from_y)

        if self.path_index == 1:
            for dx in range(-self.radius, self.radius + 1):
                for dy in range(-self.radius, self.radius + 1):
                    x = self.from_x + dx
                    y = self.from_y + dy
                    if (dx != 0 or dy != 0) and (dx ** 2 + dy ** 2 <= self.radius ** 2):
                        self.add_explosion_entity(x, y)

        if self.path_index == 2:
            for entity in self.engine.entities.all:
                if entity.distance(self.from_x, self.from_y) <= self.radius and entity.fighter:
                    results.append({'message': Message('The {0} gets burned for {1} hit points'.format(entity.name, self.damage), color_vars.spell)})
                    results.extend(entity.fighter.take_damage(self.damage))

                    distance_to_center = round(entity.distance(self.from_x, self.from_y))
                    push_distance = self.radius - distance_to_center + 2
                    animation = PushAnimation(self.engine, entity, (self.from_x, self.from_y),
                                                push_distance)
                    self.engine.animations.append(animation)

        self.path_index += 1
        if self.path_index >= 5:
            return self.complete()

        return results

    def add_explosion_entity(self, x, y):
        explosion = Entity(x, y, self.char,
                                self.color, 'Explosion',
                                render_order=RenderOrder.EFFECT)
        self.explosion_entities.append(explosion)
        self.engine.entities.append(explosion)

    def complete(self):
        self.completed = True

        for entity in self.explosion_entities:
            self.engine.entities.remove(entity)
        return []
