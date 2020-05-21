import tcod

from game_vars import map_vars, room_vars, message_vars, player_vars, color_vars
from entity_objects.map_entities import MapEntities
from game_messages import MessageLog
from game_states import GameStates
from map_objects.world.world_map import WorldMap
from map_objects.biomes.dungeon.loot import Loot

from entity_objects.entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from components.caster import Caster
from render_objects.render_order import RenderOrder


def get_game_variables():
    player = create_player()
    entities = MapEntities(player)

    dagger = Loot().get_item(0, 0, 'dagger')
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    world_map = WorldMap(map_vars.world_width, map_vars.world_height)
    world_map.make_map(entities)

    message_log = MessageLog(message_vars.x, message_vars.width, message_vars.height)

    game_state = GameStates.PLAYERS_TURN

    return entities, world_map, message_log, game_state

def create_player():
    attributes = {
        'strength': 10,
        'dexterity': 10,
        'constitution': 10,
        'intelligence': 10,
        'wisdom': 10,
        'charisma': 10,
    }
    fighter_component = Fighter(defense=player_vars.defense, power=player_vars.power)
    inventory_component = Inventory(player_vars.inventory_size)
    level_component = Level()
    equipment_component = Equipment()
    caster_component = Caster(1)
    return Entity(0, 0, player_vars.char, color_vars.player, player_vars.name, blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component, attributes=attributes, caster=caster_component)
