import tcod
import tcod.event

def handle(event):
    if event.type == 'QUIT':
        return {'exit': True}
    elif event.type == 'MOUSEMOTION':
        return {'mouseover': event.tile}
    elif event.type == 'KEYDOWN':
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

        if event.sym == tcod.event.K_RETURN and (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
            return {'fullscreen': True}
    return {}

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.tile.x, mouse.tile.y)
    names = [entity.name for entity in entities
                if entity.x == x and entity.y == y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)
    return names.capitalize()
