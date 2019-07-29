import tcod

from game_vars import map_vars, room_vars, message_vars
from entity_objects.map_entities import MapEntities
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from entity_objects.creators.player_creator import create_player
from entity_objects.creators.item_creator import create_dagger


def get_game_variables():
    player = create_player()
    entities = MapEntities(player)

    dagger = create_dagger()
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(map_vars.width, map_vars.height)
    game_map.make_map(room_vars.max_num, room_vars.min_size, room_vars.max_size,
                        map_vars.width, map_vars.height, entities)

    message_log = MessageLog(message_vars.x, message_vars.width, message_vars.height)

    game_state = GameStates.PLAYERS_TURN

    return entities, game_map, message_log, game_state
