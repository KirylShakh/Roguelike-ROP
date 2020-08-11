import math
from random import randint, choice

from map_objects.biomes.biom_map import BiomMap
from map_objects.rectangle import Rect
from entity_objects.entity import Entity
from components.stairs import Stairs, StairsDirections
from render_objects.render_order import RenderOrder
from game_vars import color_vars
from random_utils import random_choice_from_dict
from locales import locale


class CaveMap(BiomMap):
    def __init__(self, landmark=None):
        super().__init__()
        self.default_tile_blocked = True

        self.clip_iteration_number = 4
        self.grow_iteration_number = 3

        self.landmark = landmark

    # generate maze using Prim's algorithm, than remove dead ends and grow walls using cellular automata
    def make_map(self, entities, moving_down=True):
        self.generate_maze()
        self.clip_walls()
        self.grow_cave_walls()
        self.clip_walls()
        self.paint_cave()

        self.place_stairs(entities)
        self.place_player(entities.player)

    def generate_maze(self):
        # random start point for a maze
        x = randint(0, (self.owner.width - 1) // 2) * 2 + 1
        y = randint(0, (self.owner.height - 1) // 2) * 2 + 1
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


    # find any empty tile, place player there
    def place_player(self, player):
        player.x, player.y = self.stairs.x, self.stairs.y

    def place_stairs(self, entities):
        x, y = self.find_simple_empty_spot()
        stairs_component = Stairs(self.owner.dungeon_level, direction=StairsDirections.WORLD)
        self.stairs = Entity(x, y, char='<', color=color_vars.dungeon_stone['wall'],
                                name=locale.t('world.cave.passage.outside'), render_order=RenderOrder.STAIRS,
                                stairs=stairs_component)
        entities.append(self.stairs)

    def find_simple_empty_spot(self):
        for y in range(self.owner.height):
            for x in range(self.owner.width):
                if not self.owner.is_blocked(x, y):
                    return (x, y)

    # returns (bg_color, char, char_color)
    def tile_render_info(self, x, y, visible):
        tile = self.owner.tiles[x][y]
        char_object = tile.top_char_object
        bg_color = None
        fg_color = None
        char = None

        if visible:
            if 'blocked' in tile.regulatory_flags:
                bg_color = tile.bg_color()
            else:
                bg_color = tile.bg_color()
                if char_object:
                    fg_color = char_object.color
                    char = char_object.char

            tile.regulatory_flags.add('explored')
        elif 'explored' in tile.regulatory_flags:
            if 'blocked' in tile.regulatory_flags:
                bg_color = tile.bg_color_distant()
            else:
                bg_color = tile.bg_color_distant()
                if char_object:
                    fg_color = char_object.distant_color
                    char = char_object.char

        return (bg_color, char, fg_color)
