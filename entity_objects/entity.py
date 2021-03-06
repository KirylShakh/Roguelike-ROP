import math
import tcod

from components.item import Item
from render_objects.render_order import RenderOrder
from map_objects.char_object import Char

from components.attributes.strength import Strength
from components.attributes.dexterity import Dexterity
from components.attributes.constitution import Constitution
from components.attributes.intelligence import Intelligence
from components.attributes.wisdom import Wisdom
from components.attributes.charisma import Charisma

class Entity:
    def __init__(self, x, y, char=None, color=None, bg_color=None, name=None, base_name=None,
                blocks=False, render_order=RenderOrder.CORPSE,
                fighter=None, ai=None, item=None, inventory=None, stairs=None, level=None,
                equippable=None, equipment=None, attributes=None, caster=None,
                tree=None):

        self.x = x
        self.y = y
        self.char = Char(char=char, color=color, bg_color=bg_color)

        self.name = name
        self.base_name = base_name

        self.blocks = blocks
        self.render_order = render_order

        self.regulatory_flags = set()

        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equippable = equippable
        self.equipment = equipment
        self.caster = caster
        self.tree = tree

        for component in [self.fighter, self.ai, self.item, self.inventory, self.stairs, self.level,
                            self.equippable, self.equipment, self.caster, self.tree]:
            if component:
                component.own(self)

        if self.equippable and not self.item:
            item = Item()
            self.item = item
            self.item.own(self)

        if attributes:
            self.strength = Strength(attributes.get('strength', 0))
            self.dexterity = Dexterity(attributes.get('dexterity', 0))
            self.constitution = Constitution(attributes.get('constitution', 0))
            self.intelligence = Intelligence(attributes.get('intelligence', 0))
            self.wisdom = Wisdom(attributes.get('wisdom', 0))
            self.charisma = Charisma(attributes.get('charisma', 0))

            self.attributes = [self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma]

            for component in self.attributes:
                component.own(self)
        else:
            self.attributes = []

    def attribute_by_name(self, name):
        return self.__dict__.get(name, None)

    def on_turn_start(self):
        for attribute in self.attributes:
            attribute.used_in_this_turn = False

    def on_turn_end(self):
        for attribute in self.attributes:
            attribute.take_breather()

    def distance_to(self, other):
        return self.distance(other.x, other.y)

    def distance(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy)
                or entities.get_blocking_at_location(self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_astar(self, target, entities, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = tcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                tcod.map_set_properties(fov, x1, y1,
                                        'block_sight' not in game_map.tiles[x1][y1].regulatory_flags,
                                        'blocked' not in game_map.tiles[x1][y1].regulatory_flags)

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities.all:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                tcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

            # Delete the path to free memory
        tcod.path_delete(my_path)
