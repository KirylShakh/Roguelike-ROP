import tcod

from map_objects.tile import Tile
from entity_objects.map_entities import MapEntities
from game_messages import Message
from map_objects.path_functions import path_straight


class GameMap:
    def __init__(self, width, height, map_creator=None, dungeon_level=1):
        self.width = width
        self.height = height
        self.map_creator = map_creator
        self.map_creator.own(self)
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        return [[Tile(self.map_creator.default_tile_blocked) for y in range(self.height)] for x in range(self.width)]

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def make_map(self, entities, moving_down=True):
        self.tiles = self.initialize_tiles()
        self.map_creator.make_map(entities, moving_down)

    def next_floor(self, player, message_log):
        self.dungeon_level += 1
        entities = MapEntities(player)

        self.make_map(entities)

        player.fighter.heal(player.fighter.max_hp // 2)
        message_log.add_message(Message('You take a moment to rest, and recover your strength',
                                tcod.light_violet))

        return entities

    def previous_floor(self, player, message_log):
        self.dungeon_level -= 1
        entities = MapEntities(player)

        self.make_map(entities, False)

        player.fighter.heal(player.fighter.max_hp // 2)
        message_log.add_message(Message('You take a moment to rest, and recover your strength',
                                tcod.light_violet))

        return entities

    def is_path_blocked(self, path, entities):
        for x, y in path:
            if self.is_blocked(x, y) or entities.get_blocking_at_location(x, y):
                return True
        return False

    def is_void(self, x, y):
        return x < 0 or y < 0 or x >= self.width or y >= self.height

    def path_straight(self, src_x, src_y, dst_x, dst_y):
        return path_straight(src_x, src_y, dst_x, dst_y)
