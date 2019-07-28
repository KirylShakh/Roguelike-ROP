import tcod

from game_vars import map_vars, room_vars, message_vars
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment, EquipmentSlots
from components.equippable import Equippable
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from renderer_object import RenderOrder

def get_game_variables():
    fighter_component = Fighter(hp=100, defense=1, power=2)
    inventory_component = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()
    player = Entity(0, 0, '@', tcod.white, 'Me', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component, level=level_component,
                    equipment=equipment_component)
    entities = [player]

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    dagger = Entity(0, 0, '-', tcod.sky, 'Dagger', equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(map_vars.width, map_vars.height)
    game_map.make_map(room_vars.max_num, room_vars.min_size, room_vars.max_size,
                        map_vars.width, map_vars.height, player, entities)

    message_log = MessageLog(message_vars.x, message_vars.width, message_vars.height)

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state
