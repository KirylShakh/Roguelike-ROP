from action_processing.animations.move_animation import MoveAnimation
from game_messages import Message
from combat.attacks.collision_attack import CollisionAttack


class PushAnimation(MoveAnimation):
    def __init__(self, engine, entity, from_point, distance):
        super(PushAnimation, self).__init__(engine, entity)

        self.from_x, self.from_y = from_point
        self.distance = distance

        self.path = self.calculate_path()

    def complete(self):
        self.completed = True
        self.restore_entity_state()
        self.recompute_fov()
        return []

    def stop(self):
        self.completed = True

        results = []

        if hasattr(self.entity, 'fighter') and self.entity.fighter:
            attack = CollisionAttack(self.entity)
            results.extend(attack.execute())

        self.restore_entity_state()
        self.recompute_fov()

        return results

    def restore_entity_state(self):
        if 'moving' in self.entity.regulatory_flags:
            self.entity.regulatory_flags.discard('moving')
            tile = self.engine.world_map.current_dungeon.tiles[self.entity.x][self.entity.y]
            tile.place_static_entity(self.entity)
            self.engine.entities.remove(self.entity)

    def calculate_path(self):
        path = []
        if self.from_x - self.entity.x != 0:
            k = (self.from_y - self.entity.y) / (self.from_x - self.entity.x)
            b = self.from_y - k * self.from_x

            step_x = -1 if self.entity.x - self.from_x < 0 else 1
            x = self.entity.x
            for _ in range(self.distance):
                x += step_x
                y = round(k * x + b)
                path.append((x, y))
        elif self.from_y - self.entity.y != 0:
            # equation will have a view "x = b"
            k = 0
            b = self.from_x

            step_y = -1 if self.entity.y - self.from_y < 0 else 1
            y = self.entity.y
            for _ in range(self.distance):
                y += step_y
                path.append((b, y))

        # if neither is true, entity is pushed from its point nowhere, return empty push path
        return path
