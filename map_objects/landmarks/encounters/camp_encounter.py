from random import randint, choice
from enum import Enum, auto

from map_objects.landmarks.encounters.encounter import Encounter, EncounterChallenge
from map_objects.landmarks.camp import Camp
from map_objects.rectangle import Rect


class CampEncounter(Encounter):
    def init_constants(self):
        super().init_constants()

        self.min_width = 9
        self.max_width = 11

        self.min_height = 9
        self.max_height = 11

        self.minimal_map_edge_offset = 2

    def setup(self):
        if self.challenge == EncounterChallenge.EASY:
            min_number, max_number = 1, 1
        elif self.challenge == EncounterChallenge.MEDIUM:
            min_number, max_number = 2, 3
        else: #HARD
            min_number, max_number = 3, 6

        self.entity_number = randint(min_number, max_number)

    def make_landmark_objects(self):
        self.make_landmark_object('camp', self.make_camp)

    def make_camp(self):
        return Camp(self.name, self.entity_number, self)

    def place_fauna(self, game_map, entities):
        points = []
        generated = 0
        tries = 0
        while generated != self.entity_number and tries < 100:
            if randint(0, 3) > 0:
                x, y = self.rect.random_adjacent_tile(self.landmark_objects['camp'].campfire)
            else:
                x, y = self.rect.random_inside_tile()
            if not game_map.is_blocked(x, y) and not entities.find_by_point(x, y) and (x, y) not in points:
                points.append((x, y))
                generated += 1
            tries += 1

        game_map.map_creator.fauna.populate_by_type(points, 'camper', entities)

    def place_player(self, player, game_map):
        player.x, player.y = game_map.map_creator.find_simple_empty_spot()
