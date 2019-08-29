from random import choice

from random_utils import weight_factor, random_choice_from_dict
from map_objects.biomes.forest.forest_map import ForestMap
from map_objects.game_map import GameMap
from game_vars import map_vars


class ForestLocations:
    def __init__(self):
        self.locations = {
            'temple': {
                'names': [
                    'Nisswor',
                    'Shodech',
                    'Ceisess',
                    'Enransul',
                    'Veshris',
                    'Nuzough',
                    'Gartash',
                    'Sethril',
                    'Yttia',
                    'Yiatim',
                    'Quifim',
                ],
                'weight_factor': 10,
                'types': {
                    'Chapel': 30,
                    'Shrine': 10,
                    'Altar': 20,
                    'Sacred Grove': 15,
                },
            },
            'settlement': {
                'first_names': [
                    'Small',
                    'Big',
                    'Old',
                    'New',
                    'Green',
                    'Golden',
                    'Crooked',
                    '',
                ],
                'last_names': [
                    'Puzichi',
                    'Vasyuki',
                    'Boggish',
                    'Pastlakish',
                    'Pondis',
                    'Noseys',
                    'Drunkishi',
                    'Roosters',
                    'Piglets',
                    'Crawlers',
                    'Sweatses',
                    'Grumpers',
                ],
                'weight_factor': 15,
                'types': {
                    'housestead': 30,
                    'hamlet': 20,
                    'village': 10,
                },
            },
        }

    def generate_location(self):
        location_choice = random_choice_from_dict(weight_factor(self.locations))
        location = self.locations[location_choice]

        location_type = random_choice_from_dict(location['types'])
        if location_choice == 'temple':
            name = '{0} of the {1}'.format(location_type, choice(location['names']))
        elif location_choice == 'settlement':
            name = '{0} {1} {2}'.format(choice(location['first_names']), choice(location['last_names']), location_type).strip()

        landmark = Landmark(name, location_choice, location_type)
        location = GameMap(map_vars.width, map_vars.height, map_creator=ForestMap(5, landmark=landmark))
        return location

class Landmark:
    def __init__(self, name, landmark_type, landmark_subtype):
        self.name = name
        self.type = landmark_type
        self.subtype = landmark_subtype
