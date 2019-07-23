import tcod
import tcod.event

import event_handler
from renderer_object import Renderer
from map_objects.game_map import GameMap
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates

def main():
    game_name = 'tcod tutorial revised'
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50),
    }

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    root = tcod.console_init_root(screen_width, screen_height, game_name, False, tcod.RENDERER_SDL2, 'F', True)
    con = tcod.console.Console(screen_width, screen_height)
    renderer = Renderer(root, con)

    player = Entity(0, 0, '@', tcod.white, 'Me', True)
    entities = [player]

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    game_state = GameStates.PLAYERS_TURN

    while True:
        recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        renderer.render_all(entities, game_map, colors, fov_map, fov_recompute)
        fov_recompute = False

        tcod.console_flush()

        renderer.clear_all(entities)

        for event in tcod.event.wait():
            action = event_handler.handle(event)
            if action.get('exit'):
                raise SystemExit()

            move = action.get('move')
            if move and game_state == GameStates.PLAYERS_TURN:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                    if target:
                        print('You kick the ' + target.name + ' in the shins, much to its annoyance!')
                    else:
                        player.move(dx, dy)
                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

            if action.get('fullscreen'):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity != player:
                        print('The ' + entity.name + ' ponders the meaning of its existence.')

                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
