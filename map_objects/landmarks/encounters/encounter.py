from enum import Enum, auto

from map_objects.landmarks.area import LandmarkArea


class EncounterChallenge(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

class Encounter(LandmarkArea):
    def __init__(self, name, challenge=EncounterChallenge.MEDIUM, message=None):
        super().__init__(name)

        self.place_order = 'start'

        self.challenge = challenge
        self.message = message
        self.setup()

    def setup(self):
        pass

    def place_fauna(self, game_map, entities):
        pass

    def place_player(self, player, game_map):
        pass

    def create_on(self, game_map, entities):
        super().create_on(game_map)

        self.place_fauna(game_map, entities)
        self.place_player(entities.player, game_map)
