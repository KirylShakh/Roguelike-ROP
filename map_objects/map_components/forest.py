import math
from random import randint, choice

from map_objects.map_components.map_component import MapComponent
from map_objects.rectangle import Rect
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.char_object import Char


class Forest(MapComponent):
    def __init__(self, average_tree_diameter):
        self.fov_radius = 20

        self.average_tree_diameter = average_tree_diameter
        self.default_tile_blocked = False

        self.shadowed_tiles = [[]]

    def make_map(self, entities, moving_down=True):
        density = self.owner.width * self.owner.height // (self.average_tree_diameter * 2)

        self.trees = []
        primary_tree, secondary_tree, tree_colors = self.choose_forest_trees()

        for _ in range(density):
            # new tree diameter
            d = randint(1, self.average_tree_diameter * 2)
            # new tree position
            x = randint(0, self.owner.width - d - 1)
            y = randint(0, self.owner.height - d - 1)

            square_trunk = Rect(x, y, d, d)
            for tree in self.trees:
                if square_trunk.intersect(tree):
                    break
            else:
                tree_color_choice = random_choice_from_dict(tree_colors)
                tree_color = color_vars.tree_choices_colors[tree_color_choice]

                tree_info = (color_vars.tree_choices_names[tree_color_choice], tree_color, d)

                self.add_square_trunk(square_trunk, d, tree_info)
                self.trees.append(square_trunk)

        self.calculate_crowns()
        self.place_grass(primary_tree, secondary_tree)

        entities.player.x, entities.player.y = self.find_empty_spot()

    def choose_forest_trees(self):
        primary_tree_color = random_choice_from_dict(color_vars.tree_choices)
        secondary_tree_color = random_choice_from_dict(color_vars.tree_choices)
        tree_colors = dict()
        tree_colors[primary_tree_color] = 90
        tree_colors[secondary_tree_color] = 10

        primary_tree = color_vars.tree_choices_names[primary_tree_color]
        secondary_tree = color_vars.tree_choices_names[secondary_tree_color]

        return (primary_tree, secondary_tree, tree_colors)

    def find_empty_spot(self):
        center_x = int(self.owner.width / 2)
        center_y = int(self.owner.height / 2)
        checked_tiles = [[False for y in range(self.owner.height)] for x in range(self.owner.width)]

        result = self.check_empty_spot(checked_tiles, center_x, center_y, 0)
        if result:
            x, y, _ = result
            return (x, y)

        print('whoops no free space in forest')
        return (0, 0)

    def check_empty_spot(self, checked_tiles, x, y, distance):
        checked_tiles[x][y] = True
        if not self.owner.is_blocked(x, y):
            return (x, y, distance)

        deltas = [-1, 0, 1]
        for i in deltas:
            for j in deltas:
                if self.owner.is_void(x, y) or checked_tiles[x + i][y + j]:
                    continue

                result = self.check_empty_spot(checked_tiles, x + i, y + j, distance + 1)
                if result:
                    _, _, distance = result
                    if distance < self.average_tree_diameter * 2:
                        return result

        return None

    # function fills structures like this (example for square with side = 5 which has 2 options)
    # --+--  -+++-
    # -+++-  +++++
    # +++++  +++++
    # -+++-  +++++
    # --+--  -+++-
    def add_square_trunk(self, square_trunk, diameter, tree_info):
        if diameter < 4:
            self.add_small_square_trunk(square_trunk, tree_info)
            return

        num_of_tree_options = math.ceil(diameter / 2) - 1
        option = randint(1, num_of_tree_options)

        y = square_trunk.y1 + 1 # starting with first row
        first_row_width = option * 2 if diameter % 2 == 0 else option * 2 - 1
        number_of_tiles_in_row = first_row_width

        # filling upper halfsphere until we hit completely solid rows
        while number_of_tiles_in_row != diameter:
            row_start_tile = (diameter - number_of_tiles_in_row) // 2 + 1
            row_end_tile = row_start_tile + number_of_tiles_in_row

            for x in range(square_trunk.x1 + row_start_tile - 1, square_trunk.x1 + row_end_tile - 1):
                self.make_tree_tile(x, y, tree_info)

            y += 1
            number_of_tiles_in_row += 2

        # filling rows that are fully solid
        lower_halfsphere_row = y + first_row_width
        while y != lower_halfsphere_row:
            for x in range(square_trunk.x1, square_trunk.x2):
                self.make_tree_tile(x, y, tree_info)
            y += 1

        # filling lower halfsphere
        while number_of_tiles_in_row > first_row_width:
            number_of_tiles_in_row -= 2
            row_start_tile = (diameter - number_of_tiles_in_row) // 2 + 1
            row_end_tile = row_start_tile + number_of_tiles_in_row

            for x in range(square_trunk.x1 + row_start_tile - 1, square_trunk.x1 + row_end_tile - 1):
                self.make_tree_tile(x, y, tree_info)

            y += 1

    def add_small_square_trunk(self, square_trunk, tree_info):
        for x in range(square_trunk.x1, square_trunk.x2):
            for y in range(square_trunk.y1, square_trunk.y2):
                self.make_tree_tile(x, y, tree_info)

    def make_tree_tile(self, x, y, tree_info):
        tile = self.owner.tiles[x][y]
        tile.block()

        tree_name, tree_color, diameter = tree_info

        if diameter < 4:
            name = 'Trunk of {0}'.format(tree_name)
        else:
            name = 'Giant trunk of {0}'.format(tree_name)

        tile.char = Char(name=name, color=tree_color)

    def calculate_crowns(self):
        self.shadowed_tiles = [[False for y in range(self.owner.height)] for x in range(self.owner.width)]

        for x in range(self.owner.width):
            for y in range(self.owner.height):
                if self.tile_is_under_crown(x, y):
                    self.shadowed_tiles[x][y] = True

    def tile_is_under_crown(self, x, y):
        for tree in self.trees:
            tree_diameter = tree.x2 - tree.x1
            center_x, center_y = tree.center()
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

            if distance <= tree_diameter + 1:
                return True

        return False

    def place_grass(self, primary_tree, secondary_tree):
        grass_chars = {
            '.': 40,
            ',': 35,
            ';': 25,
            ':': 20,
            '\'': 35,
            '"': 30,
            '`': 35,
            '~': 35,
            'Y': 15,
            'T': 10,
            '|': 10,
            '\\': 7,
            '/': 7,
            ' ': 5,
        }

        shadowed_grass_chars = dict(grass_chars, **{
            'Y': 5,
            'T': 3,
            '|': 3,
            '\\': 2,
            '/': 2,
            ' ': 10,
        })

        grass_chars_names = {
            '.': 'Sprout of Aposeris',
            ',': 'Sprout of Astrancia',
            ';': 'Sprout of Astilboides',
            ':': 'Sprout of Helleborus',
            '\'': 'Sprout of Tricyrtis',
            '"': 'Shrub of Vaccinium',
            '`': 'Sprout of Bergenia',
            '~': 'Shrub of Juniperus',
            'Y': 'Sapling of {0}'.format(primary_tree),
            'T': 'Sapling of {0}'.format(secondary_tree),
            '|': 'Withered sapling of {0}'.format(primary_tree),
            '\\': 'Withered sapling of {0}'.format(primary_tree),
            '/': 'Withered sapling of {0}'.format(secondary_tree),
            ' ': 'Patch of soil',
        }

        for x in range(self.owner.width):
            for y in range(self.owner.height):
                if not self.owner.is_blocked(x, y):
                    if self.shadowed_tiles[x][y]:
                        grass_char_symbol = random_choice_from_dict(shadowed_grass_chars)
                    else:
                        grass_char_symbol = random_choice_from_dict(grass_chars)

                    grass_char_color_choice = random_choice_from_dict(color_vars.grass_choices)
                    grass_char_color = color_vars.grass_choices_colors[grass_char_color_choice]

                    grass_name = grass_chars_names[grass_char_symbol]
                    if not self.shadowed_tiles[x][y]:
                        grass_name += ' on a sunny glade'

                    self.owner.tiles[x][y].char = Char(char=grass_char_symbol, color=grass_char_color, name=grass_name)

    def place_entities(self, square, entities):
        pass

    # (bg_color, char, char_color)
    def tile_render_info(self, x, y, visible):
        bg_color = color_vars.soil
        char = None
        char_color = None

        if visible:
            if self.owner.is_blocked(x, y):
                bg_color = self.owner.tiles[x][y].char.color
            else:
                char_obj = self.owner.tiles[x][y].char

                if self.shadowed_tiles[x][y]:
                    char, char_color = (char_obj.char, char_obj.shadow_color)
                else:
                    char, char_color = (char_obj.char, char_obj.color)

            self.owner.tiles[x][y].explored = True
        elif self.owner.tiles[x][y].explored:
            if self.owner.is_blocked(x, y):
                bg_color = self.owner.tiles[x][y].char.distant_color
            else:
                char_obj = self.owner.tiles[x][y].char

                if self.shadowed_tiles[x][y]:
                    char, char_color = (char_obj.char, char_obj.distant_shadow_color)
                else:
                    char, char_color = (char_obj.char, char_obj.distant_color)

        return (bg_color, char, char_color)
