import tcod
import tcod.event

def handle(event):
    if event.type == 'QUIT':
        return {'exit': True}
    elif event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}

        if event.sym == tcod.event.K_UP:
            return {'move': (0, -1)}
        elif event.sym == tcod.event.K_DOWN:
            return {'move': (0, 1)}
        elif event.sym == tcod.event.K_LEFT:
            return {'move': (-1, 0)}
        elif event.sym == tcod.event.K_RIGHT:
            return {'move': (1, 0)}

        if event.sym == tcod.event.K_RETURN and (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
            return {'fullscreen': True}
    return {}
