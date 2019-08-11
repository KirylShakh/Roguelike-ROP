from enum import Enum, auto

from components.component import Component

class StairsDirections(Enum):
    DOWN = auto()
    UP = auto()
    WORLD = auto()

class Stairs(Component):
    def __init__(self, floor, direction=StairsDirections.DOWN):
        self.floor = floor
        self.direction = direction
