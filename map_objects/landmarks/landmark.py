from random import randint

from map_objects.rectangle import Rect


class Landmark:
    def __init__(self, name, parent=None):
        self.name = name

        self.min_width = 4
        self.max_width = 6

        self.min_height = 4
        self.max_height = 6

        self.minimal_map_edge_offset = 5

        self.parent = parent

    def make_rect(self, map_width, map_height):
        # random width and height
        w = randint(self.min_width, self.max_width)
        h = randint(self.min_height, self.max_height)
        # random position without going out of the boundaries of the map
        x = randint(self.minimal_map_edge_offset, map_width - w - self.minimal_map_edge_offset - 1)
        y = randint(self.minimal_map_edge_offset, map_height - h - self.minimal_map_edge_offset - 1)

        return Rect(x, y, w, h, calculate_borders=True)

    def create_on(self, game_map):
        self.rect = self.make_rect(game_map.width, game_map.height)
