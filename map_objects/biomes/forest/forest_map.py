import math
from random import randint

from map_objects.biomes.biom_map import BiomMap
from map_objects.rectangle import Rect
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.biomes.forest.flora import Flora
from map_objects.biomes.forest.fauna import Fauna


class ForestMap(BiomMap):
    def __init__(self, average_tree_diameter, landmark=None):
        self.fov_radius = 20

        self.landmark = landmark
        self.average_tree_diameter = average_tree_diameter
        self.flora = Flora(self.average_tree_diameter)
        self.fauna = Fauna()

        self.default_tile_blocked = False

        self.shadowed_tiles = [[]]

    def make_map(self, entities, moving_down=True):
        if self.landmark:
            self.place_landmark()
        self.place_trees()
        self.calculate_crowns()
        self.place_grass()
        self.place_entities(entities)

        self.place_player(entities.player)

    def place_player(self, player):
        player.x, player.y = self.find_empty_spot()

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

    def place_landmark(self):
        self.landmark.create_on(self.owner)

    def place_entities(self, entities):
        # self.fauna.populate(self.owner, entities)
        pass

    def place_trees(self):
        density = self.owner.width * self.owner.height // (self.average_tree_diameter * 2)

        self.trees = []

        for _ in range(density):
            new_tree = self.flora.get_tree()
            # new tree diameter
            # new tree position
            x = randint(0, self.owner.width - new_tree.diameter - 1)
            y = randint(0, self.owner.height - new_tree.diameter - 1)

            square_trunk = Rect(x, y, new_tree.diameter, new_tree.diameter)
            if self.landmark and self.landmark.rect.intersect_with_additional_space(square_trunk):
                continue
            for tree in self.trees:
                if square_trunk.intersect(tree.trunk):
                    break
            else:
                new_tree.set_trunk(square_trunk)
                self.draw_tree(new_tree)
                self.trees.append(new_tree)

    # function fills structures like this (example for square with side = 5 which has 2 options)
    # --+--  -+++-
    # -+++-  +++++
    # +++++  +++++
    # -+++-  +++++
    # --+--  -+++-
    def draw_tree(self, tree):
        if tree.diameter < 4:
            self.draw_small_tree(tree)
            return

        num_of_tree_options = math.ceil(tree.diameter / 2) - 1
        option = randint(1, num_of_tree_options)

        y = tree.trunk.y1 + 1 # starting with first row
        first_row_width = option * 2 if tree.diameter % 2 == 0 else option * 2 - 1
        number_of_tiles_in_row = first_row_width

        # filling upper halfsphere until we hit completely solid rows
        while number_of_tiles_in_row != tree.diameter:
            row_start_tile = (tree.diameter - number_of_tiles_in_row) // 2 + 1
            row_end_tile = row_start_tile + number_of_tiles_in_row

            for x in range(tree.trunk.x1 + row_start_tile - 1, tree.trunk.x1 + row_end_tile - 1):
                self.make_tree_tile(x, y, tree)

            y += 1
            number_of_tiles_in_row += 2

        # filling rows that are fully solid
        lower_halfsphere_row = y + first_row_width
        while y != lower_halfsphere_row:
            for x in range(tree.trunk.x1, tree.trunk.x2):
                self.make_tree_tile(x, y, tree)
            y += 1

        # filling lower halfsphere
        while number_of_tiles_in_row > first_row_width:
            number_of_tiles_in_row -= 2
            row_start_tile = (tree.diameter - number_of_tiles_in_row) // 2 + 1
            row_end_tile = row_start_tile + number_of_tiles_in_row

            for x in range(tree.trunk.x1 + row_start_tile - 1, tree.trunk.x1 + row_end_tile - 1):
                self.make_tree_tile(x, y, tree)

            y += 1

    def draw_small_tree(self, tree):
        for x in range(tree.trunk.x1, tree.trunk.x2):
            for y in range(tree.trunk.y1, tree.trunk.y2):
                self.make_tree_tile(x, y, tree)

    def make_tree_tile(self, x, y, tree):
        tree.x = x
        tree.y = y

        tile = self.owner.tiles[x][y]
        tile.block()
        tile.place_static_entity(tree)

    def calculate_crowns(self):
        self.shadowed_tiles = [[False for y in range(self.owner.height)] for x in range(self.owner.width)]

        for x in range(self.owner.width):
            for y in range(self.owner.height):
                if self.tile_is_under_crown(x, y):
                    self.shadowed_tiles[x][y] = True

    def tile_is_under_crown(self, x, y):
        for tree in self.trees:
            center_x, center_y = tree.trunk.center()
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

            if distance <= tree.diameter + 1:
                return True

        return False

    def place_grass(self):
        for x in range(self.owner.width):
            for y in range(self.owner.height):
                if not self.owner.is_blocked(x, y) and not self.owner.tiles[x][y].static_entities:
                    self.owner.tiles[x][y].place_static_entity(self.flora.get_tile_plant(x, y, self.shadowed_tiles[x][y]))

    # (bg_color, char, char_color)
    def tile_render_info(self, x, y, visible):
        tile = self.owner.tiles[x][y]
        bg_color = color_vars.soil
        char = None
        char_color = None

        if visible:
            if self.owner.is_blocked(x, y):
                if tile.top_char_object:
                    char, char_color = (tile.top_char_object.char, tile.top_char_object.shadow_color)
            else:
                if self.shadowed_tiles[x][y]:
                    char, char_color = (tile.top_char_object.char, tile.top_char_object.shadow_color)
                else:
                    char, char_color = (tile.top_char_object.char, tile.top_char_object.color)
            bg_color = tile.bg_color()

            tile.regulatory_flags.add('explored')
        elif 'explored' in tile.regulatory_flags:
            if self.owner.is_blocked(x, y):
                if tile.top_char_object:
                    char, char_color = (tile.top_char_object.char, tile.top_char_object.distant_shadow_color)
                bg_color = tile.bg_color_distant()
            else:
                if self.shadowed_tiles[x][y]:
                    char, char_color = (tile.top_char_object.char, tile.top_char_object.distant_shadow_color)
                else:
                    char, char_color = (tile.top_char_object.char, tile.top_char_object.distant_color)
            bg_color = tile.bg_color_distant()

        return (bg_color, char, char_color)
