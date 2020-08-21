import math
from random import randint, choice

from map_objects.biomes.biom_map import BiomMap
from map_objects.biomes.dungeon.flora import Flora
from map_objects.biomes.dungeon.fauna import Fauna
from map_objects.rectangle import Rect
from map_objects.path_functions import find_path_in_area
from entity_objects.entity import Entity
from components.stairs import Stairs, StairsDirections
from render_objects.render_order import RenderOrder
from game_vars import color_vars
from random_utils import random_choice_from_dict
from fov_functions import get_fov_coordinates_from_point
from locales import locale


class CaveMap(BiomMap):
    def __init__(self, landmark=None):
        super().__init__()
        self.default_tile_blocked = True

        self.clip_iteration_number = 4
        self.grow_iteration_number = 3

        self.landmark = landmark

        self.flora = Flora()
        self.fauna = Fauna()

    # map generation method: it will generate map, paint tiles, divide map into zones, place entities (flora, fauna, etc.)
    # map generation sequence: generate maze using Prim's algorithm, than remove dead ends and grow walls using cellular automata
    def make_map(self, entities, moving_down=True):
        self.moving_down = moving_down
        self.generate_maze()
        self.clip_walls()
        self.grow_cave_walls()
        self.clip_walls()
        self.paint_cave()

        self.place_stairs(entities)
        self.place_player(entities.player)

        self.split_into_zones()
        self.fauna.populate_cave(self.owner, entities)

    def generate_maze(self):
        # random start point for a maze
        x = randint(0, (self.owner.width - 1) // 2) * 2
        y = randint(0, (self.owner.height - 1) // 2) * 2
        self.owner.tiles[x][y].unblock()

        # initial check tiles 2 spaces from start
        to_check = []
        for px, py in [(x, y - 2), (x, y + 2), (x - 2, y), (x + 2, y)]:
            if not self.owner.is_void(px, py):
                to_check.append((px, py))

        while len(to_check) > 0:
            cell = choice(to_check)
            to_check.remove(cell)

            x, y = cell
            if not self.owner.is_blocked(x, y):
                continue
            self.owner.tiles[x][y].unblock()

            # check tiles 2 spaces from chosen and create a bridge to first such one
            directions = ['north', 'south', 'east', 'west']
            direction_conf = {
                'north': {
                    'destination_cell': (x, y - 2),
                    'bridge_cell': (x, y - 1),
                },
                'south': {
                    'destination_cell': (x, y + 2),
                    'bridge_cell': (x, y + 1),
                },
                'east': {
                    'destination_cell': (x - 2, y),
                    'bridge_cell': (x - 1, y),
                },
                'west': {
                    'destination_cell': (x + 2, y),
                    'bridge_cell': (x + 1, y),
                },
            }
            while len(directions) > 0:
                direction = choice(directions)
                dest_x, dest_y = direction_conf[direction]['destination_cell']

                if not self.owner.is_void(dest_x, dest_y) and not self.owner.is_blocked(dest_x, dest_y):
                    bridge_x, bridge_y = direction_conf[direction]['bridge_cell']
                    self.owner.tiles[bridge_x][bridge_y].unblock()

                    directions.clear()
                    break

                directions.remove(direction)

            # add wall tiles 2 spaces from chosen
            for px, py in [(x, y - 2), (x, y + 2), (x - 2, y), (x + 2, y)]:
                if not self.owner.is_void(px, py) and self.owner.is_blocked(px, py):
                    to_check.append((px, py))

    def clip_walls(self):
        max_neighbours = 1
        for _ in range(self.clip_iteration_number):
            dead_ends = []
            for y in range(self.owner.height):
                for x in range(self.owner.width):
                    if not self.owner.is_blocked(x, y):
                        neighbours = 0
                        for px, py in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]:
                            if not self.owner.is_void(px, py) and not self.owner.is_blocked(px, py):
                                neighbours += max_neighbours
                        if neighbours <= 1:
                            dead_ends.append((x, y))

            for x, y in dead_ends:
                self.owner.tiles[x][y].block()

    def grow_cave_walls(self):
        min_neighbours = 4
        for _ in range(self.grow_iteration_number):
            new_cells = []
            for y in range(self.owner.height):
                for x in range(self.owner.width):
                    if self.owner.is_blocked(x, y):
                        neighbours = 0
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                px = x + dx
                                py = y + dy
                                if not self.owner.is_void(px, py) and not self.owner.is_blocked(px, py):
                                    neighbours += 1

                        if neighbours >= min_neighbours:
                            new_cells.append((x, y))

            for cell_x, cell_y in new_cells:
                self.owner.tiles[cell_x][cell_y].unblock()

    def paint_cave(self):
        for x in range(self.owner.width):
            for y in range(self.owner.height):
                tile = self.owner.tiles[x][y]
                if 'blocked' in tile.regulatory_flags:
                    tile.set_bg_color(color_vars.dungeon_stone['wall'])
                else:
                    tile.set_bg_color(color_vars.dungeon_stone['floor'])

    def place_player(self, player):
        if self.moving_down:
            player.x, player.y = self.up_stairs.x, self.up_stairs.y
        else:
            player.x, player.y = self.down_stairs.x, self.down_stairs.y

    def place_stairs(self, entities):
        if self.owner.dungeon_level == 1:
            direction = StairsDirections.WORLD
            name = locale.t('world.cave.passage.outside')
        else:
            direction = StairsDirections.UP
            name = locale.t('world.cave.passage.upside')
        x, y = self.find_simple_empty_spot()
        stairs_component = Stairs(self.owner.dungeon_level, direction=direction)
        self.up_stairs = Entity(x, y, char='<', color=color_vars.dungeon_stone['wall'],
                                name=name, render_order=RenderOrder.STAIRS,
                                stairs=stairs_component)
        entities.append(self.up_stairs)

        x, y = self.find_simple_empty_spot()
        stairs_component = Stairs(self.owner.dungeon_level + 1)
        self.down_stairs = Entity(x, y, char='>', color=color_vars.dungeon_stone['wall'],
                                name=locale.t('world.cave.passage.downside'), render_order=RenderOrder.STAIRS,
                                stairs=stairs_component)
        entities.append(self.down_stairs)

        if self.up_stairs.x == self.down_stairs.x and self.up_stairs.y == self.down_stairs.y:
            self.up_stairs.char.char = '&'
            self.down_stairs.char.char = '&'

    def split_into_zones(self):
        self.entrance_zones = []
        self.twilight_zone = set()
        self.dark_zone = set()

        self.evaluate_entrance_zones()
        self.flora.grow_cave_entrance_zone(self.owner, self.entrance_zones)
        self.light_entrance_zones()

        self.evaluate_twilight_and_dark_zones()
        self.flora.grow_cave_twilight_zone(self.owner, self.twilight_zone)
        self.flora.grow_cave_dark_zone(self.owner, self.dark_zone)

    def evaluate_entrance_zones(self):
        if self.owner.dungeon_level == 1:
            # this is top level of caves, means it should have entrance to surface and therefore have entrance zone
            x, y = self.up_stairs.x, self.up_stairs.y
            entrance_zone = {
                'center': (x, y),
                'coords': get_fov_coordinates_from_point(self.owner, x, y),
            }
            self.entrance_zones.append(entrance_zone)

            # chance to contain another entrance which is a hole in the cave cellar
            x, y = randint(0, self.owner.width), randint(0, self.owner.height)
            if self.owner.is_empty(x, y):
                entrance_zone = {
                    'center': (x, y),
                    'coords': get_fov_coordinates_from_point(self.owner, x, y),
                }
                self.entrance_zones.append(entrance_zone)

    def light_entrance_zones(self):
        for entrance_zone in self.entrance_zones:
            for x, y in entrance_zone['coords']:
                self.owner.tiles[x][y].light_up()

    def evaluate_twilight_and_dark_zones(self):
        entrance_zone_tiles = set()
        for entrance_zone in self.entrance_zones:
            entrance_zone_tiles |= entrance_zone['coords']

        for y in range(self.owner.height):
            for x in range(self.owner.width):
                if self.owner.is_blocked(x, y):
                    continue

                if self.entrance_zones or self.owner.dungeon_level == 2:
                    if not (x, y) in entrance_zone_tiles:
                        self.twilight_zone.add((x, y))
                else:
                    self.dark_zone.add((x, y))

    # returns (bg_color, char, char_color)
    def tile_render_info(self, x, y, visible):
        tile = self.owner.tiles[x][y]
        char_object = tile.top_char_object
        bg_color = None
        fg_color = None
        char = None

        if visible:
            bg_color = tile.bg_color()
            if char_object:
                fg_color = char_object.color
                char = char_object.char

            tile.regulatory_flags.add('explored')
        elif 'explored' in tile.regulatory_flags:
            bg_color = tile.bg_color_distant()
            if char_object:
                fg_color = char_object.distant_color
                char = char_object.char

        return (bg_color, char, fg_color)
