import tcod
import tcod.event

import event_handler
from renderer_object import Renderer
from map_objects.game_map import GameMap
from entity import Entity

def main():
    game_name = 'tcod tutorial revised'
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150)
    }

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    root = tcod.console_init_root(screen_width, screen_height, game_name, False, tcod.RENDERER_SDL2, 'F', True)
    con = tcod.console.Console(screen_width, screen_height)
    renderer = Renderer(root, con)

    game_map = GameMap(map_width, map_height)

    player = Entity(int(screen_width / 2), int(screen_height / 2), tcod.event.K_AT, tcod.white)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), tcod.event.K_AT, tcod.yellow)
    entities = [player, npc]

    while True:
        renderer.render_all(entities, game_map, colors)
        tcod.console_flush()

        renderer.clear_all(entities)

        for event in tcod.event.wait():
            action = event_handler.handle(event)
            if action.get('exit'):
                raise SystemExit()

            move = action.get('move')
            if move:
                dx, dy = move
                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    player.move(dx, dy)

            if action.get('fullscreen'):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


if __name__ == '__main__':
    main()
