import tcod

from map_objects.landmarks.shed import Shed
from map_objects.char_object import Char
from game_vars import color_vars


class Hut(Shed):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.bed_char = Char(char='-', color=color_vars.wood, name='Bed in {0}'.format(name))
        self.table_char = Char(char='=', color=color_vars.wood, name='Table in {0}'.format(name))

    def make_objects(self):
        super().make_objects()
        self.make_furniture()

    def make_windows(self):
        self.windows = []
        window_number = len(self.rect.sides[self.door_side_direction])

        for _ in range(0, window_number):
            window = self.rect.random_side_tile()
            while window == self.door:
                window = self.rect.random_side_tile()

            if not self.corner_wall_tile(window):
                self.windows.append(window)

    def make_furniture(self):
        bed_x, bed_y = self.rect.random_inside_tile(direction=self.door_side_direction)
        table_x, table_y = self.rect.random_inside_tile(direction=self.door_side_direction)
        while (table_x, table_y) == (bed_x, bed_y):
            table_x, table_y = self.rect.random_inside_tile(direction=self.door_side_direction)
        self.furniture = [(bed_x, bed_y, self.bed_char), (table_x, table_y, self.table_char)]

    def place(self, game_map):
        super().place(game_map)

        for (x, y, char) in self.furniture:
            game_map.tiles[x][y].blocked = False
            game_map.tiles[x][y].block_sight = False
            game_map.tiles[x][y].char = char

    def corner_wall_tile(self, tile):
        x, y = tile
        adj_horiz_walls = 0
        if (x + 1, y) in self.walls:
            adj_horiz_walls += 1
        if (x - 1, y) in self.walls:
            adj_horiz_walls += 1

        adj_vert_walls = 0
        if (x, y + 1) in self.walls:
            adj_vert_walls += 1
        if (x, y - 1) in self.walls:
            adj_vert_walls += 1

        return adj_horiz_walls == 1 or adj_vert_walls == 1
