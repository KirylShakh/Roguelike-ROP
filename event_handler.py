import tcod
import tcod.event

def handle(event):
    if event.type == 'QUIT':
        return {'exit': True}
    elif event.type == 'KEYDOWN':
        if event.sym == tcod.event.K_ESCAPE:
            return {'exit': True}
        elif event.sym == tcod.event.K_UP:
            return {'move': (0, -1)}
    return {}
