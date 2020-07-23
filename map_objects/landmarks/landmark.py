from random import randint

from map_objects.rectangle import Rect


class Landmark:
    def __init__(self, name, parent=None):
        self.name = name

        self.init_constants()

        if parent:
            self.set_parent_rect(parent.rect)
            self.make_rect()
        else:
            self.rect = None

    def init_constants(self):
        self.min_width = 4
        self.max_width = 6

        self.min_height = 4
        self.max_height = 6

        self.minimal_map_edge_offset = 5

    def setup_map_boundaries(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x + self.minimal_map_edge_offset
        self.max_x = max_x - self.minimal_map_edge_offset - 1

        self.min_y = min_y + self.minimal_map_edge_offset
        self.max_y = max_y - self.minimal_map_edge_offset - 1

    def set_parent_rect(self, rect):
        self.setup_map_boundaries(rect.x1, rect.x2, rect.y1, rect.y2)

    def make_rect(self):
        # random width and height
        w = randint(self.min_width, self.max_width)
        h = randint(self.min_height, self.max_height)
        # random position without going out of the boundaries of the map/parent rect
        x = randint(self.min_x, self.max_x - w)
        y = randint(self.min_y, self.max_y - h)

        self.rect = Rect(x, y, w, h, calculate_borders=True)

    def create_on(self, game_map):
        if not self.rect:
            self.setup_map_boundaries(0, game_map.width, 0, game_map.height)
            self.make_rect()
