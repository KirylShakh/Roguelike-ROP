from random import randint
from enum import Enum, auto

from map_objects.landmarks.encounters.encounter import Encounter, EncounterChallenge


class SurroundEncounter(Encounter):
    def __init__(self, name, challenge=EncounterChallenge.MEDIUM, message=None, entity_type='bandit'):
        super().__init__(name, challenge=challenge, message=message)
        self.entity_type = entity_type

    def init_constants(self):
        super().init_constants()

        self.min_width = 10
        self.max_width = 20

        self.min_height = 10
        self.max_height = 15

    def setup(self):
        self.place_order = 'end'

        if self.challenge == EncounterChallenge.EASY:
            min_number, max_number = 1, 3
        elif self.challenge == EncounterChallenge.MEDIUM:
            min_number, max_number = 3, 6
        else: #HARD
            min_number, max_number = 6, 12

        self.entity_number = randint(min_number, max_number)

    def place_fauna(self, game_map, entities):
        points = []
        generated = 0
        tries = 0
        while generated != self.entity_number and tries < 100:
            x, y = self.rect.random_border_tile()
            if not game_map.is_blocked(x, y) and not entities.find_by_point(x, y) and (x, y) not in points:
                points.append((x, y))
                generated += 1
            tries += 1

        game_map.map_creator.fauna.populate_by_type(points, self.entity_type, entities)

    def place_player(self, player, game_map):
        player.x, player.y = game_map.map_creator.find_empty_spot(self.rect)
