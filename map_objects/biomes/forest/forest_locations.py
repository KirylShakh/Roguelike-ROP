from random import randint, choice
import tcod

from random_utils import weight_factor, random_choice_from_dict
from game_vars import map_vars
from map_objects.biomes.forest.forest_map import ForestMap
from map_objects.game_map import GameMap
from map_objects.landmarks.chapel import Chapel
from map_objects.landmarks.shrine import Shrine
from map_objects.landmarks.shed import Shed
from map_objects.landmarks.hut import Hut
from map_objects.landmarks.house import House
from map_objects.landmarks.housestead import Housestead


class ForestLocations:
    def __init__(self):
        self.locations = {
            'temple': {
                'names': [
                    'Nisswor', # Goddess
                    'Shodech', # God
                    'Ceisess', # Goddess of Pain, Suffering, Endurance, mother of Veshris
                    'Enransul', # God of Pride, Priviledge, War, father of Veshris
                    'Veshris', # God of Solitude, Piece, Rot, son of Enransul
                    'Nuzough', # God of Life, Fertility, Nature
                    'Gartash', # God of Creation, Perfection, Madness
                    'Sethril', # Goddess of Freedom, Violence, Feasts
                    'Yttia', # Supreme Goddess of Memories, Ocean, Void, sister of Yiatim
                    'Yiatim', # Supreme God of Change, Sky, Ways, brother of Yttia
                    'Quifim', # Goddess of Love, Lies, Regret
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
                    'hut': 10,
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

        landmark = self.generate_landmark(name, location_choice, location_type)
        location = GameMap(map_vars.width, map_vars.height, map_creator=ForestMap(5, landmark=landmark))
        return location

    def generate_landmark(self, name, location_choice, location_type):
        if location_choice == 'temple':
            if location_type == 'Shrine':
                return Shrine(name)
            elif location_type == 'Chapel':
                return Chapel(name)
        elif location_choice == 'settlement':
            if location_type == 'hut':
                return Hut(name)
            elif location_type == 'housestead':
                return Housestead(name)

        return Housestead(name)
