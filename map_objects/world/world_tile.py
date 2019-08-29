import tcod

# Merge this with Tile class
class WorldTile:
    def __init__(self, biom, char, color, bg_color=tcod.black):
        self.biom = biom
        self.explored = False
        self.visited = False
        self.locations = None

        self.char = char
        self.color = color
        self.bg_color = bg_color

        self.distant_color = self.get_distant_color(color)
        self.distant_bg_color = self.get_distant_color(bg_color)

    def get_distant_color(self, color):
        return tcod.Color(
            color.r  - int(color.r * 0.5),
            color.g - int(color.g * 0.5),
            color.b - int(color.b * 0.5)
        )
