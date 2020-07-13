import math

from render_objects.render_order import RenderOrder
from map_objects.char_object import Char


class StaticEntity:
    def __init__(self, x, y, char=None, color=None, bg_color=None, name=None, base_name=None,
                blocks=False, render_order=RenderOrder.CORPSE):
        self.x = x
        self.y = y
        self.char = Char(char=char, color=color, bg_color=bg_color)

        self.name = name
        self.base_name = base_name

        self.blocks = blocks
        self.render_order = render_order

        self.regulatory_flags = set()

    def distance_to(self, other):
        return self.distance(other.x, other.y)

    def distance(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)