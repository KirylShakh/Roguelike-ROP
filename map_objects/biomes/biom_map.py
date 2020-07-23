from random import choice

from components.component import Component
from random_utils import random_choice_from_dict, weight_factor
from map_objects.landmarks.encounters.encounter import EncounterChallenge


class BiomMap(Component):
    def __init__(self):
        self.fov_radius = 10
        self.encounter = None

    def choose_encounter(self):
        possible_encounters = self.possible_encounters()
        if not possible_encounters:
            return False

        challenge = choice(list(EncounterChallenge))

        encounter_choices = weight_factor(possible_encounters)
        encounter_choice = random_choice_from_dict(encounter_choices)
        encounter_conf = possible_encounters[encounter_choice]

        self.encounter = encounter_conf['class'](encounter_choice, challenge=challenge, **encounter_conf['parameters'])
        return True

    def possible_encounters(self):
        return {}

    def find_empty_spot(self, rect, location='center'):
        if location == 'center':
            desired_x, desired_y = rect.center()
        elif location == 'side':
            desired_x, desired_y = rect.random_border_tile()

        checked_tiles = [[False for y in range(0, rect.y2)] for x in range(0, rect.x2)]

        result = self.check_empty_spot(checked_tiles, desired_x, desired_y, 0)
        if result:
            x, y, _ = result
            return (x, y)

        print('whoops no free space on map')
        return (0, 0)

    def check_empty_spot(self, checked_tiles, x, y, distance):
        checked_tiles[x][y] = True
        if not self.owner.is_blocked(x, y):
            return (x, y, distance)

        deltas = [-1, 0, 1]
        for i in deltas:
            for j in deltas:
                if self.owner.is_void(x, y) or checked_tiles[x + i][y + j] or (i == 0 and j == 0):
                    continue

                result = self.check_empty_spot(checked_tiles, x + i, y + j, distance + 1)
                if result:
                    if self._map_specific_empty_spot_check(result):
                        return result

        return None

    def _map_specific_empty_spot_check(self, result):
        return True
