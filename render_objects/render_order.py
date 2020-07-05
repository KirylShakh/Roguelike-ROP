from enum import Enum, auto


class RenderOrder(Enum):
    SMALL_OBJECTS = auto()
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
    EFFECT = auto()
