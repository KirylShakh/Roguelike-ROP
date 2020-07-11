import tcod

from map_objects.landmarks.shed import Shed
from entity_objects.static_entity import StaticEntity


class Chapel(Shed):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.altar_char = {'char': tcod.CHAR_RADIO_UNSET, 'color': tcod.grey, 'name': 'Altar of {0}'.format(name)}

    def make_objects(self):
        super().make_objects()
        self.make_altar()

    def make_windows(self):
        window = self.rect.random_side_tile()
        while window == self.door:
            window = self.rect.random_side_tile()

        self.windows = [window]

    def make_altar(self):
        self.altar = [self.rect.random_inside_tile(direction=self.door_side_direction)]

    def place(self, game_map):
        super().place(game_map)

        for (x, y) in self.altar:
            game_map.tiles[x][y].block()
            game_map.tiles[x][y].place_static_entity(StaticEntity(x, y, **self.altar_char))
