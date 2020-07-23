from random import randint
import tcod

from map_objects.landmarks.landmark import Landmark
from entity_objects.entity import Entity
from render_objects.render_order import RenderOrder
from game_vars import color_vars


class Camp(Landmark):
    def __init__(self, name, number_of_campers=1, parent=None):
        super().__init__(name, parent=parent)

        self.number_of_campers = number_of_campers

        self.campfire_char = {'char': '#', 'color': tcod.lightest_orange, 'name': 'Campfire at {0}'.format(name.title()), 'render_order': RenderOrder.ITEM}
        self.tent_char = {'char': '^', 'color': tcod.Color(40, 28, 11), 'name': 'Tent at {0}'.format(name)}
        self.bench_char = {'char': '_', 'color': tcod.dark_grey, 'name': 'Bench at {0}'.format(name)}

    def init_constants(self):
        super().init_constants()

        self.minimal_map_edge_offset = 1

    def create_on(self, game_map):
        super().create_on(game_map)

        self.make_objects()
        self.place(game_map)

    def make_objects(self):
        self.make_campfire()
        self.make_tents()
        self.make_benches()

    def make_campfire(self):
        self.campfire = self.rect.center()

    def make_tents(self):
        self.tents = []
        tent_number = max(0, randint(self.number_of_campers // 2 - 2, self.number_of_campers // 2 + 1))
        for _ in range(tent_number):
            self.tents.append(self.rect.random_border_tile())

    def make_benches(self):
        self.benches = []
        bench_number = max(0, randint(self.number_of_campers // 2 - 2, self.number_of_campers // 2 + 1))
        for _ in range(bench_number):
            self.benches.append(self.rect.random_inside_tile())

    def place(self, game_map):
        x, y = self.campfire
        game_map.tiles[x][y].unblock()
        game_map.tiles[x][y].clear_static_entities()
        game_map.tiles[x][y].place_static_entity(Entity(x, y, **self.campfire_char))

        for x, y in self.tents:
            game_map.tiles[x][y].block()
            game_map.tiles[x][y].clear_static_entities()
            game_map.tiles[x][y].place_static_entity(Entity(x, y, **self.tent_char))

        for x, y in self.benches:
            game_map.tiles[x][y].clear_static_entities()
            game_map.tiles[x][y].place_static_entity(Entity(x, y, **self.bench_char))
