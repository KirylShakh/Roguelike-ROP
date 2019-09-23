from map_objects.landmarks.landmark import Landmark
from map_objects.landmarks.house import House
from map_objects.landmarks.hut import Hut
from map_objects.landmarks.shed import Shed
from map_objects.char_object import Char
from game_vars import color_vars


class Housestead(Landmark):
    def __init__(self, name):
        super(Housestead, self).__init__(name)

        self.min_width = 21
        self.max_width = 40

        self.min_height = 21
        self.max_height = 40

        self.road_char = Char(char='+', color=color_vars.wood, name='Road in {0}'.format(name))

    def create_on(self, game_map):
        self.rect = self.make_rect(game_map.width, game_map.height)
