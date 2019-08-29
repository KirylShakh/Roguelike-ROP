from random import choice

from random_utils import weight_factor, random_choice_from_dict
from map_objects.biomes.dungeon.dungeon_map import DungeonMap
from map_objects.game_map import GameMap
from game_vars import map_vars


class DungeonLocations:
    def __init__(self):
        self.locations = {
            'city': {
                'names': [
                    'Queeg',
                    'Dray',
                    'Toitight-ran',
                ],
                'weight_factor': 10,
                'types': {
                    'Manor': 20,
                    'Guildhall': 10,
                    'Prison': 10,
                    'Temple': 20,
                    'Slums': 5,
                },
            },
            'cave': {
                'names': [
                    'Untnal',
                    'Nar',
                    'Lacon',
                ],
                'weight_factor': 25,
                'types': {
                    'Catacomb': 30,
                    'Ruin': 20,
                    'Cavern': 10,
                },
            },
        }

    def generate_location(self):
        location_choice = random_choice_from_dict(weight_factor(self.locations))
        location = self.locations[location_choice]

        location_type = random_choice_from_dict(location['types'])
        if location_choice == 'city':
            name = 'Remains of {0} of the city of {1}'.format(location_type, choice(location['names']))
        elif location_choice == 'cave':
            name = '{0} of {1}'.format(location_type, choice(location['names'])).strip()

        landmark = Landmark(name, location_choice, location_type)
        location = GameMap(map_vars.width, map_vars.height, map_creator=DungeonMap(10, 3, 5, landmark=landmark))
        return location

class Landmark:
    def __init__(self, name, landmark_type, landmark_subtype):
        self.name = name
        self.type = landmark_type
        self.subtype = landmark_subtype

    def place_landmark(self, game_map):
        pass
