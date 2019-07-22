import tcod
import tcod.event

import event_handler

def main():
    screen_width = 80
    screen_height = 50
    game_name = 'tcod tutorial revised'
    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(screen_width, screen_height, game_name, False, tcod.RENDERER_SDL2, 'F', True)
    con = tcod.console_new(screen_width, screen_height)

    while True:
        tcod.console_put_char(con, player_x, player_y, '@', tcod.BKGND_NONE)
        tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
        tcod.console_flush()

        tcod.console_put_char(con, player_x, player_y, ' ', tcod.BKGND_NONE)

        for event in tcod.event.wait():
            action = event_handler.handle(event)
            if action.get('exit'):
                raise SystemExit()

            move = action.get('move')
            if move:
                dx, dy = move
                player_x += dx
                player_y += dy

            if action.get('fullscreen'):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())



if __name__ == '__main__':
    main()
