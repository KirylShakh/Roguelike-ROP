from fov_functions import recompute_fov


# abstract base class for more detailed move animations
class MoveAnimation(object):
    def __init__(self, engine, entity):
        self.engine = engine
        self.entity = entity

        self.path = []
        self.path_index = 0
        self.completed = False

    def next_tick(self):
        if self.path_index >= len(self.path) or self.completed:
            return []

        x, y = self.path[self.path_index]
        if (self.engine.world_map.current_dungeon.is_blocked(x, y)
                    or self.engine.entities.get_blocking_at_location(x, y)):
            # path became blocked. for now simply stopping moving
            return self.stop()
        else:
            self.entity.x = x
            self.entity.y = y

        self.path_index += 1
        if self.path_index == len(self.path):
            return self.complete()

        return []

    def complete(self):
        self.completed = True
        self.recompute_fov()
        return []

    def stop(self):
        self.completed = True
        self.recompute_fov()
        return []

    def recompute_fov(self):
        player = self.engine.entities.player
        if self.entity == player:
            fov_radius = self.engine.world_map.current_dungeon.map_creator.fov_radius
            recompute_fov(self.engine.fov_map, player.x, player.y, fov_radius)
            self.engine.fov_recompute = True
