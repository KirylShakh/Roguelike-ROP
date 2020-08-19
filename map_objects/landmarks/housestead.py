import math
from random import randint

from map_objects.landmarks.area import LandmarkArea
from map_objects.landmarks.house import House
from map_objects.landmarks.hut import Hut
from map_objects.landmarks.shed import Shed
from map_objects.landmarks.kitchen_garden import KitchenGarden
from map_objects.path_functions import find_path_in_area
from entity_objects.entity import Entity
from game_vars import color_vars
from random_utils import random_choice_from_dict


class Housestead(LandmarkArea):
    def __init__(self, name):
        super().__init__(name)

        self.road_char = {'char': '+', 'color': color_vars.dirt_road, 'name': 'Road in {0}'.format(name)}
        self.fence_char = {'char': '#', 'color': color_vars.dirt_road, 'name': 'Fence in {0}'.format(name)}
        self.gate_char = {'char': '/', 'color': color_vars.dirt_road, 'name': 'Gates in {0}'.format(name)}

    def make_landmark_objects(self):
        # family house
        main_hold = random_choice_from_dict({
            'house': 70,
            'hut': 30,
        })
        if main_hold == 'house':
            main_hold_method = self.make_house
        else:
            main_hold_method = self.make_hut
        self.make_landmark_object('main_hold', main_hold_method)

        # sheds
        self.make_landmark_object('shed', self.make_shed)

        # kitchen-garden
        self.make_landmark_object('kitchen-garden', self.make_kitchen_garden)

    def make_house(self):
        return House('Family house in {0}'.format(self.name), parent=self)

    def make_hut(self):
        return Hut('Hut in {0}'.format(self.name), parent=self)

    def make_shed(self):
        return Shed('Shed in {0}'.format(self.name), parent=self)

    def make_kitchen_garden(self):
        return KitchenGarden('Kitchen-garden in {0}'.format(self.name), parent=self)

    def make_fence(self, game_map):
        main_gate_direction, main_gate = self.rect.random_direction_side_tile()
        back_gate_direction = self.rect.opposite_direction(main_gate_direction)
        _, back_gate = self.rect.random_direction_side_tile(back_gate_direction)

        fence_tiles = self.rect.border_tiles + self.rect.corner_tiles
        fence_tiles.remove(main_gate)
        fence_tiles.remove(back_gate)

        self.place_mozaic_objects(fence_tiles, game_map, self.fence_char, 99, True)
        game_map.tiles[main_gate[0]][main_gate[1]].place_static_entity(Entity(main_gate[0], main_gate[1], **self.gate_char))
        game_map.tiles[back_gate[0]][back_gate[1]].place_static_entity(Entity(back_gate[0], back_gate[1], **self.gate_char))

        self.fence_tiles = fence_tiles
        self.main_gate = main_gate
        self.back_gate = back_gate

    def make_road(self, game_map):
        path = []
        if 'shed' in self.landmark_objects:
            # road between household and shed
            path += self.build_road_section(self.landmark_objects['main_hold'].door, self.landmark_objects['shed'].door, game_map)
            # road betweeen shed and main gate
            path += self.build_road_section(self.landmark_objects['shed'].door, self.main_gate, game_map)
            # road between shed and back gate
            path += self.build_road_section(self.landmark_objects['shed'].door, self.back_gate, game_map)

        # road betweeen household and main gate
        path += self.build_road_section(self.landmark_objects['main_hold'].door, self.main_gate, game_map)
        # road between household and back gate
        path += self.build_road_section(self.landmark_objects['main_hold'].door, self.back_gate, game_map)

        road = [(x + self.rect.x1, y + self.rect.y1) for x, y in path]
        self.place_mozaic_objects(road, game_map, self.road_char, 70)

    def build_road_section(self, start_tile, end_tile, game_map):
        start_x, start_y = start_tile
        end_x, end_y = end_tile

        return find_path_in_area(
            (start_x - self.rect.x1, start_y - self.rect.y1),
            (end_x - self.rect.x1, end_y - self.rect.y1),
            self.are_map_for_road_building(game_map)
        )

    def are_map_for_road_building(self, game_map):
        return [[-1 if self.can_be_road(game_map, x + self.rect.x1, y + self.rect.y1) else -2 for y in range(self.rect.h)] for x in range(self.rect.w)]

    def can_be_road(self, game_map, x, y):
        return (not game_map.is_blocked(x, y)
                and 'indoor' not in game_map.tiles[x][y].regulatory_flags
                and 'cultivated' not in game_map.tiles[x][y].regulatory_flags)

    def place_mozaic_objects(self, obj_list, game_map, obj_char, place_chance, blocked = False, block_sight = False):
        place_choices = {
            'place': place_chance,
            'dont': 100 - place_chance,
        }

        for (x, y) in obj_list:
            if random_choice_from_dict(place_choices) == 'place':
                game_map.tiles[x][y].place_static_entity(Entity(x, y, **obj_char))
                if blocked:
                    game_map.tiles[x][y].regulatory_flags.add('blocked')
                if block_sight:
                    game_map.tiles[x][y].regulatory_flags.add('block_sight')

    def create_on(self, game_map):
        super().create_on(game_map)

        # fence and gates
        self.make_fence(game_map)
        # road
        self.make_road(game_map)
