from enum import Enum, auto


class RenderOrder(Enum):
    FLOOR = auto()
    TINY_OBJECTS = auto()
    SMALL_OBJECTS = auto()
    GROUND_FLORA = auto()
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
    EFFECT = auto()
