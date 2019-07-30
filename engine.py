import tcod
import tcod.event

from game_vars import screen_vars, fov_vars, panel_vars, menu_vars, map_vars, room_vars
import event_handler
from render_objects.renderer import Renderer
from fov_functions import initialize_fov, recompute_fov, initialize_world_fov, recompute_world_fov
from game_states import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message
from loader_functions.initialize_new_game import get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from map_objects.game_map import GameMap


def main():
    renderer = Renderer()
    renderer.render_root()

    entities = None
    world_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = tcod.image_load(screen_vars.menu_background_img)

    while True:
        if show_main_menu:
            main_menu(main_menu_background_image, menu_vars.main_width, renderer)

            for event in tcod.event.wait():
                if show_load_error_message:
                    message_box('No save game to load', 50, renderer)

                tcod.console_flush()

                action = event_handler.handle_main_menu(event)
                new_game = action.get('new_game')
                load_saved_game = action.get('load_saved_game')
                exit_game = action.get('exit_game')

                if show_load_error_message and (new_game or load_saved_game or exit_game):
                    show_load_error_message = False
                elif new_game:
                    entities, world_map, message_log, game_state = get_game_variables()
                    show_main_menu = False
                    break
                elif load_saved_game:
                    try:
                        entities, world_map, message_log, game_state = load_game()
                        show_main_menu = False
                        break
                    except FileNotFoundError:
                        show_load_error_message = True
                elif exit_game:
                    raise SystemExit
        else:
            renderer.clear()
            if not world_map.current_dungeon:
                play_game(entities, world_map, message_log, game_state, renderer)
            else:
                enter_dungeon(entities, world_map, message_log, game_state, renderer)
            show_main_menu = True

def play_game(entities, world_map, message_log, game_state, renderer):
    fov_recompute = True
    fov_map = initialize_world_fov(world_map)

    player = entities.player
    whats_under_mouse = ''
    previous_game_state = game_state

    while True:
        if fov_recompute:
            recompute_world_fov(fov_map, player.x, player.y)

        renderer.render_world(entities, world_map, fov_map, fov_recompute,
                            message_log, whats_under_mouse, game_state)
        fov_recompute = False

        tcod.console_flush()

        renderer.clear_all(entities)

        for event in tcod.event.wait():
            player_turn_results = []

            action = event_handler.handle(event, game_state)
            if action.get('exit'):
                if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                    game_state = previous_game_state
                elif game_state == GameStates.TARGETING:
                    player_turn_results.append({'targeting_cancelled': True})
                else:
                    save_game(entities, world_map, message_log, game_state)
                    return True

            if action.get('wait'):
                game_state = GameStates.ENEMY_TURN

            move = action.get('move')
            if move and game_state == GameStates.PLAYERS_TURN:
                dx, dy = move

                if not world_map.is_void(player.x + dx, player.y + dy):
                    player.move(dx, dy)
                    fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

            if action.get('show_inventory'):
                previous_game_state = game_state
                game_state = GameStates.SHOW_INVENTORY

            if action.get('drop_inventory'):
                previous_game_state = game_state
                game_state = GameStates.DROP_INVENTORY

            if action.get('show_character_screen'):
                previous_game_state = game_state
                game_state = GameStates.CHARACTER_SCREEN

            if action.get('take_stairs_down') and game_state == GameStates.PLAYERS_TURN:
                tile = world_map.tiles[player.x][player.y]
                if tile.biom == 'dungeon':
                    game_map = GameMap(map_vars.width, map_vars.height)
                    game_map.make_map(room_vars.max_num, room_vars.min_size, room_vars.max_size,
                                        entities)
                    world_map.current_dungeon = game_map

                    renderer.clear()
                    enter_dungeon(entities, world_map, message_log, game_state, renderer)
                    return True
                else:
                    message_log.add_message(Message('There are no dungeons nearbye', tcod.yellow))

            if action.get('fullscreen'):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            mouseover_tile = action.get('mouseover')
            if mouseover_tile:
                (x, y) = (mouseover_tile.x, mouseover_tile.y)
                if not world_map.is_void(x, y) and fov_map.fov[x][y]:
                    whats_under_mouse = world_map.tiles[x][y].biom.capitalize()

            if game_state == GameStates.ENEMY_TURN:
                tile = world_map.tiles[player.x][player.y]
                if not tile.visited:
                    if tile.biom == 'forest':
                        message_log.add_message(Message('You traverse empty lifeless silent forest'))
                    elif tile.biom == 'dungeon':
                        message_log.add_message(Message('There are bottomless ruins here'))
                    tile.visited = True
                game_state = GameStates.PLAYERS_TURN

def enter_dungeon(entities, world_map, message_log, game_state, renderer):
    game_map = world_map.current_dungeon

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    previous_game_state = game_state

    entities_under_mouse = ''
    targeting_item = None
    player = entities.player

    while True:
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y)

        renderer.render_all(entities, game_map, fov_map, fov_recompute,
                            message_log, entities_under_mouse, game_state)
        fov_recompute = False

        tcod.console_flush()

        renderer.clear_all(entities)

        for event in tcod.event.wait():
            player_turn_results = []

            action = event_handler.handle(event, game_state)
            if action.get('exit'):
                if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                    game_state = previous_game_state
                elif game_state == GameStates.TARGETING:
                    player_turn_results.append({'targeting_cancelled': True})
                else:
                    save_game(entities, world_map, message_log, game_state)
                    return True

            if action.get('wait'):
                game_state = GameStates.ENEMY_TURN

            move = action.get('move')
            if move and game_state == GameStates.PLAYERS_TURN:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    target = entities.get_blocking_at_location(destination_x, destination_y)

                    if target:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    else:
                        player.move(dx, dy)
                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

            pickup = action.get('pickup')
            if pickup and game_state == GameStates.PLAYERS_TURN:
                for entity in entities.all:
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

            if action.get('show_character_screen'):
                previous_game_state = game_state
                game_state = GameStates.CHARACTER_SCREEN

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

            if action.get('take_stairs_down') and game_state == GameStates.PLAYERS_TURN:
                for entity in entities.all:
                    if entity.stairs and entity.x == player.x and entity.y == player.y:
                        entities = game_map.next_floor(player, message_log)
                        fov_map = initialize_fov(game_map)
                        fov_recompute = True
                        renderer.clear()
                        break
                else:
                    message_log.add_message(Message('There are no stairs here', tcod.yellow))

            level_up = action.get('level_up')
            if level_up:
                if level_up == 'hp':
                    player.fighter.base_max_hp += 20
                    player.fighter.heal(20)
                elif level_up == 'str':
                    player.fighter.base_power += 1
                elif level_up == 'def':
                    player.fighter.base_defense += 1

                game_state = previous_game_state

            if action.get('fullscreen'):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            mouseover_tile = action.get('mouseover')
            if mouseover_tile:
                (x, y) = (mouseover_tile.x, mouseover_tile.y)
                entities_under_mouse = [entity.name for entity in entities.all
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

                equip = player_turn_result.get('equip')
                if equip:
                    equip_results = player.equipment.toggle_equip(equip)
                    for equip_result in equip_results:
                        equipped = equip_result.get('equipped')
                        if equipped:
                            message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                        dequipped = equip_result.get('dequipped')
                        if dequipped:
                            message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                    game_state = GameStates.ENEMY_TURN

                targeting = player_turn_result.get('targeting')
                if targeting:
                    previous_game_state = GameStates.PLAYERS_TURN
                    game_state = GameStates.TARGETING

                    targeting_item = targeting

                    message_log.add_message(targeting_item.item.targeting_message)

                xp = player_turn_result.get('xp')
                if xp:
                    leveled_up = player.level.add_xp(xp)
                    message_log.add_message(Message('You gain {0} experience points'.format(xp)))

                    if leveled_up:
                        message_log.add_message(
                            Message('Your battle skills grow stronger. You reached level {0}'.format(player.level.current_level),
                            tcod.yellow)
                        )
                        previous_game_state = game_state
                        game_state = GameStates.LEVEL_UP

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities.all:
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
