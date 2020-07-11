import tcod

from map_objects.landmarks.landmark import Landmark
from entity_objects.static_entity import StaticEntity
from render_objects.render_order import RenderOrder
from game_vars import color_vars


class Shed(Landmark):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.wall_char = {'bg_color': tcod.darkest_grey, 'name': name}
        self.door_char = {'char': '/', 'color': tcod.lightest_grey, 'name': 'Door to {0}'.format(name)}
        self.window_char = {'char': tcod.CHAR_BLOCK1, 'color': tcod.lightest_grey, 'name': 'Window to {0}'.format(name)}
        self.floor_char = {'char': '.', 'color': tcod.darker_gray, 'name': 'Floor of {0}'.format(name), 'render_order': RenderOrder.FLOOR}

    def init_constants(self):
        super().init_constants()

        self.minimal_map_edge_offset = 2

    def create_on(self, game_map):
        super().create_on(game_map)

        self.make_objects()
        self.place(game_map)

    def make_objects(self):
        self.make_walls()
        self.make_door()
        self.make_windows()

    def make_walls(self):
        self.walls = self.rect.border_tiles

    def make_door(self):
        self.door_side_direction, self.door = self.rect.random_direction_side_tile()

    def make_windows(self):
        _, window = self.rect.random_direction_side_tile(self.door_side_direction)
        while window == self.door:
            _, window = self.rect.random_direction_side_tile(self.door_side_direction)

        self.windows = [window]

    def place(self, game_map):
        for x, y in self.walls:
            game_map.tiles[x][y].block()
            game_map.tiles[x][y].place_static_entity(StaticEntity(x, y, **self.wall_char))

        x, y = self.door
        game_map.tiles[x][y].unblock()
        game_map.tiles[x][y].clear_static_entities()
        game_map.tiles[x][y].place_static_entity(StaticEntity(x, y, **self.door_char))

        for (x, y) in self.windows:
            game_map.tiles[x][y].regulatory_flags.add('blocked')
            game_map.tiles[x][y].regulatory_flags.discard('block_sight')
            game_map.tiles[x][y].clear_static_entities()
            game_map.tiles[x][y].place_static_entity(StaticEntity(x, y, **self.window_char))

        for x in range(self.rect.x1 + 1, self.rect.x2 - 1):
            for y in range(self.rect.y1 + 1, self.rect.y2 - 1):
                if not game_map.tiles[x][y].static_entities:
                    game_map.tiles[x][y].place_static_entity(StaticEntity(x, y, **self.floor_char))
                    game_map.tiles[x][y].regulatory_flags.add('indoor')
