import tcod
import tcod.event

from game_states import GameStates

def handle(event, game_state):
    if event.type == 'QUIT':
        return {'exit': True}
    elif event.type == 'MOUSEMOTION':
        return {'mouseover': event.tile}

    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn(event)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead(event)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_show_inventory(event)

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

        if event.sym == tcod.event.K_g:
            return {'pickup': True}
        elif event.sym == tcod.event.K_i:
            return {'show_inventory': True}
        elif event.sym == tcod.event.K_d:
            return {'drop_inventory': True}

        if event.sym == tcod.event.K_RETURN and (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
            return {'fullscreen': True}

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