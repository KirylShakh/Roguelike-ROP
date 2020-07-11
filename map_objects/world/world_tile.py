from game_vars import color_vars
from map_objects.tile import Tile


class WorldTile(Tile):
    def __init__(self, biom=None, blocked=False, block_sight = None, bg_color = color_vars.default_bg):
        super().__init__(blocked=blocked, block_sight=block_sight, bg_color=bg_color)

        self.biom = biom
        self.locations = None
