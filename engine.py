import tcod
import tcod.event

import event_handler
from renderer_object import Renderer, RenderOrder
from map_objects.game_map import GameMap
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message

def main():
    game_name = 'tcod tutorial revised'
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 43

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 5
    max_items_per_room = 3

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
    renderer = Renderer(root, con, screen_width, screen_height)

    panel = tcod.console.Console(screen_width, panel_height)

    message_log = MessageLog(message_x, message_width, message_height)
    entities_under_mouse = ''

    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', tcod.white, 'Me', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component)
    entities = [player]

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height,
                        player, entities, max_monsters_per_room, max_items_per_room)

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None

    while True:
        recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        renderer.render_all(entities, player, game_map, colors, fov_map, fov_recompute,
                            panel, bar_width, panel_height, panel_y, message_log,
                            entities_under_mouse, game_state)
        fov_recompute = False

        tcod.console_flush()

        renderer.clear_all(entities)

        for event in tcod.event.wait():
            action = event_handler.handle(event, game_state)
            if action.get('exit'):
                if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                    game_state = previous_game_state
                elif game_state == GameStates.TARGETING:
                    player_turn_results.append({'targeting_cancelled': True})
                else:
                    raise SystemExit()

            player_turn_results = []

            move = action.get('move')
            if move and game_state == GameStates.PLAYERS_TURN:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                    if target:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    else:
                        player.move(dx, dy)
                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

            pickup = action.get('pickup')
            if pickup and game_state == GameStates.PLAYERS_TURN:
                for entity in entities:
                    if entity.item and entity.x == player.x and entity.y == player.y:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)
                        break
                else:
                    message_log.add_message(Message('There is nothing to pick up here', tcod.yellow))

            if action.get('show_inventory'):
                previous_game_state = game_state
                game_state = GameStates.SHOW_INVENTORY

            inventory_index = action.get('inventory_index')
            if (inventory_index is not None
                        and previous_game_state != GameStates.PLAYER_DEAD
                        and inventory_index < len(player.inventory.items)):
                item = player.inventory.items[inventory_index]

                if game_state == GameStates.SHOW_INVENTORY:
                    player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
                elif game_state == GameStates.DROP_INVENTORY:
                    player_turn_results.extend(player.inventory.drop_item(item))

            if action.get('drop_inventory'):
                previous_game_state = game_state
                game_state = GameStates.DROP_INVENTORY

            left_click = action.get('left_click')
            right_click = action.get('right_click')
            if game_state == GameStates.TARGETING:
                if left_click:
                    target_x, target_y = left_click
                    item_use_results = player.inventory.use(targeting_item, entities=entities,
                                        fov_map=fov_map, target_x=target_x, target_y=target_y)
                    player_turn_results.extend(item_use_results)
                elif right_click:
                    player_turn_results.append({'targetting_cancelled': True})

            if action.get('fullscreen'):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            mouseover_tile = action.get('mouseover')
            if mouseover_tile:
                (x, y) = (mouseover_tile.x, mouseover_tile.y)
                entities_under_mouse = [entity.name for entity in entities
                            if entity.x == x and entity.y == y and fov_map.fov[entity.x][entity.y]]
                entities_under_mouse = ', '.join(entities_under_mouse).capitalize()

            for player_turn_result in player_turn_results:
                message = player_turn_result.get('message')
                if message:
                    message_log.add_message(message)

                targeting_cancelled = player_turn_result.get('targeting_cancelled')
                if targeting_cancelled:
                    game_state = previous_game_state
                    message_log.add_message(Message('Targeting cancelled'))

                dead_entity = player_turn_result.get('dead')
                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(player)
                    else:
                        message = kill_monster(dead_entity)

                    message_log.add_message(message)

                item_added = player_turn_result.get('item_added')
                if item_added:
                    entities.remove(item_added)
                    game_state = GameStates.ENEMY_TURN

                item_consumed = player_turn_result.get('consumed')
                if item_consumed:
                    game_state = GameStates.ENEMY_TURN

                item_dropped = player_turn_result.get('item_dropped')
                if item_dropped:
                    entities.append(item_dropped)
                    game_state = GameStates.ENEMY_TURN

                targeting = player_turn_result.get('targeting')
                if targeting:
                    previous_game_state = GameStates.PLAYERS_TURN
                    game_state = GameStates.TARGETING

                    targeting_item = targeting

                    message_log.add_message(targeting_item.item.targeting_message)

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')

                            if message:
                                message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, game_state = kill_player(player)
                                else:
                                    message = kill_monster(dead_entity)

                                message_log.add_message(message)

                                if game_state == GameStates.PLAYER_DEAD:
                                    break

                        if game_state == GameStates.PLAYER_DEAD:
                            break
                else:
                    game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
