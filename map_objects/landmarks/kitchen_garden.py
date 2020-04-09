import tcod

from random_utils import random_choice_from_dict

from map_objects.landmarks.landmark import Landmark
from map_objects.char_object import Char
from game_vars import color_vars


class KitchenGarden(Landmark):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.plant_chars = {
            'turnip': Char(char='t', color=tcod.light_yellow, name='Turnip sprout'),
            'potato': Char(char='p', color=tcod.light_green, name='Potato sprout'),
            'tomato': Char(char='p', color=tcod.light_red, name='Tomato sprout'),
            'beetroot': Char(char='b', color=tcod.dark_red, name='Beetroot sprout'),
        }

    def init_constants(self):
        self.min_width = 3
        self.max_width = 8

        self.min_height = 3
        self.max_height = 8

        self.minimal_map_edge_offset = 1

    def create_on(self, game_map):
        super().create_on(game_map)

        self.make_beds()
        self.place_on(game_map)

    def make_beds(self):
        plant_choices = {
            'turnip': 25,
            'potato': 30,
            'tomato': 25,
            'beetroot': 25,
        }
        number_of_beds = self.rect.h if self.rect.h < self.rect.w else self.rect.w
        self.beds = [random_choice_from_dict(plant_choices) for _ in range(number_of_beds)]

    def place_on(self, game_map):
        bed = 0
        if self.rect.h < self.rect.w:
            for y in range(self.rect.y1, self.rect.y2):
                for x in range(self.rect.x1, self.rect.x2):
                    game_map.tiles[x][y].char = self.plant_chars[self.beds[bed]]
                    game_map.tiles[x][y].cultivated = True
                bed += 1
        else:
            for x in range(self.rect.x1, self.rect.x2):
                for y in range(self.rect.y1, self.rect.y2):
                    game_map.tiles[x][y].char = self.plant_chars[self.beds[bed]]
                    game_map.tiles[x][y].cultivated = True
                bed += 1
