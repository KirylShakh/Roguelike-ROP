import os
import shelve

def save_game(entities, world_map, message_log, game_state):
    with shelve.open('savegame', 'n') as data_file:
        data_file['entities'] = entities
        data_file['world_map'] = world_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state

def load_game():
    if not os.path.isfile('savegame.dat'):
        raise FileNotFoundError

    with shelve.open('savegame', 'r') as data_file:
        entities = data_file['entities']
        world_map = data_file['world_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    return entities, world_map, message_log, game_state
