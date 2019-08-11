import tcod
import tcod.event

from game_states import GameStates

def handle(event, game_state):
    if event.type == 'QUIT':
        return {'exit': True}
    elif event.type == 'MOUSEMOTION':
        return {'mouseover': event.tile}
    elif event.type == 'MOUSEBUTTONUP':
        if event.button == tcod.event.BUTTON_LEFT:
            return {'left_click': (event.tile.x, event.tile.y)}
        elif event.button == tcod.event.BUTTON_RIGHT:
            return {'right_click': (event.tile.x, event.tile.y)}

    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn(event)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead(event)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_show_inventory(event)
    elif game_state == GameStates.TARGETING:
        return handle_targeting(event)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(event)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(event)

    return {}

def handle_player_turn(event):
    if event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}

        if event.sym == tcod.event.K_UP or event.sym == tcod.event.K_k:
            return {'move': (0, -1)}
        elif event.sym == tcod.event.K_DOWN or event.sym == tcod.event.K_j:
            return {'move': (0, 1)}
        elif event.sym == tcod.event.K_LEFT or event.sym == tcod.event.K_h:
            return {'move': (-1, 0)}
        elif event.sym == tcod.event.K_RIGHT or event.sym == tcod.event.K_l:
            return {'move': (1, 0)}
        elif event.sym == tcod.event.K_y:
            return {'move': (-1, -1)}
        elif event.sym == tcod.event.K_u:
            return {'move': (1, -1)}
        elif event.sym == tcod.event.K_b:
            return {'move': (-1, 1)}
        elif event.sym == tcod.event.K_n:
            return {'move': (1, 1)}
        elif event.sym == tcod.event.K_z:
            return {'wait': True}

        if event.sym == tcod.event.K_g:
            return {'pickup': True}
        elif event.sym == tcod.event.K_i:
            return {'show_inventory': True}
        elif event.sym == tcod.event.K_d:
            return {'drop_inventory': True}
        elif event.sym == tcod.event.K_c:
            return {'show_character_screen': True}

        if event.sym == tcod.event.K_PERIOD and (tcod.event.KMOD_LSHIFT or tcod.event.KMOD_RSHIFT):
            return {'take_stairs_down': True}
        elif event.sym == tcod.event.K_COMMA and (tcod.event.KMOD_LSHIFT or tcod.event.KMOD_RSHIFT):
            return {'take_stairs_up': True}

        if event.sym == tcod.event.K_RETURN and (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
            return {'fullscreen': True}

        # test
        if event.sym == tcod.event.K_f:
            return {'cast_fireball': True}

    return {}

def handle_player_dead(event):
    if event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}

        if event.sym == tcod.event.K_i:
            return {'show_inventory': True}

        if event.sym == tcod.event.K_RETURN and (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
            return {'fullscreen': True}

    return {}

def handle_show_inventory(event):
    if event.type == 'KEYDOWN':
        index = event.sym - ord('a')
        if index >= 0:
            return {'inventory_index': index}

        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}

        if event.sym == tcod.event.K_RETURN and (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
            return {'fullscreen': True}

    return {}

def handle_targeting(event):
    if event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}
    return {}

def handle_main_menu(event):
    if event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_a:
            return {'new_game': True}
        elif event.sym == tcod.event.K_b:
            return {'load_saved_game': True}
        elif event.sym == tcod.event.K_c or event.sym == tcod.event.K_ESCAPE:
            return {'exit_game': True}
    return {}

def handle_level_up_menu(event):
    if event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_a:
            return {'level_up': 'hp'}
        elif event.sym == tcod.event.K_b:
            return {'level_up': 'str'}
        elif event.sym == tcod.event.K_c:
            return {'level_up': 'def'}
    return {}

def handle_character_screen(event):
    if event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}
    return {}
