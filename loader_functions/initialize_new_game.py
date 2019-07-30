import tcod

from game_vars import map_vars, room_vars, message_vars
from entity_objects.map_entities import MapEntities
from game_messages import MessageLog
from game_states import GameStates
from map_objects.world.world_map import WorldMap
from entity_objects.creators.player_creator import create_player
from entity_objects.creators.item_creator import create_dagger


def get_game_variables():
    player = create_player()
    entities = MapEntities(player)

    dagger = create_dagger()
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    world_map = WorldMap(map_vars.world_width, map_vars.world_height)
    world_map.make_map(entities)

    message_log = MessageLog(message_vars.x, message_vars.width, message_vars.height)

    game_state = GameStates.PLAYERS_TURN

    return entities, world_map, message_log, game_state
