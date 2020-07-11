import tcod

from map_objects.landmarks.chapel import Chapel
from entity_objects.static_entity import StaticEntity
from game_vars import color_vars


class Shrine(Chapel):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.vertical_bench_char = {'char': '|', 'color': color_vars.wood, 'name': 'Small bench'}
        self.horizontal_bench_char = {'char': '-', 'color': color_vars.wood, 'name': 'Small bench'}

    def init_constants(self):
        super().init_constants()

        self.min_width = 6
        self.max_width = 12

        self.min_height = 6
        self.max_height = 12

    def make_objects(self):
        super().make_objects()
        self.make_benches()

    def make_door(self):
        self.door_side_direction, door_side = self.rect.random_short_side()
        self.door = door_side[len(door_side) // 2]

    def make_windows(self):
        window_sides = self.rect.neighbour_sides(self.door_side_direction)

        self.windows = []
        for i in range(1, len(window_sides[0]), 2):
            for side in window_sides:
                self.windows.append(side[i])

    def make_altar(self):
        if self.door_side_direction in ['east', 'west']:
            even_side = (self.rect.y2 - self.rect.y1) % 2 == 0
            _, y = self.rect.center()
            x = self.rect.x2 - 4 if self.door_side_direction == 'west' else self.rect.x1 + 3

            altar_tiles = [(x, y - 1), (x, y), (x, y + 1)]
            if even_side:
                altar_tiles.append((x, y - 2))
        else:
            even_side = (self.rect.x2 - self.rect.x1) % 2 == 0
            x, _ = self.rect.center()
            y = self.rect.y2 - 4 if self.door_side_direction == 'north' else self.rect.y1 + 3

            altar_tiles = [(x - 1, y), (x, y), (x + 1, y)]
            if even_side:
                altar_tiles.append((x - 2, y))

        self.altar = altar_tiles

    def make_benches(self):
        if self.door_side_direction in ['east', 'west']:
            if self.door_side_direction == 'west':
                x1 = self.rect.x1 + 2
                x2 = self.rect.x2 - 6
            else:
                x1 = self.rect.x1 + 6
                x2 = self.rect.x2 - 2

            _, center_y = self.rect.center()
            even_side = (self.rect.y2 - self.rect.y1) % 2 == 0
            if even_side:
                start_y = self.rect.y1 + 2
                end_y = self.rect.y2 - 2
                passage = [center_y, center_y - 1]
            else:
                start_y = self.rect.y1 + 3
                end_y = self.rect.y2 - 3
                passage = [center_y]

            xs = [x for x in range(x1, x2, 2)]
            ys = [y for y in range(start_y, end_y) if y not in passage]

            bench_char = self.vertical_bench_char
        else:
            if self.door_side_direction == 'north':
                y1 = self.rect.y1 + 2
                y2 = self.rect.y2 - 6
            else:
                y1 = self.rect.y1 + 6
                y2 = self.rect.y2 - 2

            center_x, _ = self.rect.center()
            even_side = (self.rect.x2 - self.rect.x1) % 2 == 0
            if even_side:
                start_x = self.rect.x1 + 2
                end_x = self.rect.x2 - 2
                passage = [center_x, center_x - 1]
            else:
                start_x = self.rect.x1 + 3
                end_x = self.rect.x2 - 3
                passage = [center_x]

            xs = [x for x in range(start_x, end_x) if x not in passage]
            ys = [y for y in range(y1, y2, 2)]

            bench_char = self.horizontal_bench_char

        self.benches = (bench_char, [(x, y) for x in xs for y in ys])

    def place(self, game_map):
        super().place(game_map)

        bench_char, bench_tiles = self.benches
        for (x, y) in bench_tiles:
            game_map.tiles[x][y].regulatory_flags.add('blocked')
            game_map.tiles[x][y].regulatory_flags.discard('block_sight')
            game_map.tiles[x][y].place_static_entity(StaticEntity(x, y, **bench_char))
