import tcod

from locales import locale


def menu(header, options, width, renderer):
    if len(options) > 26:
        raise ValueError('Cannot have more than 26 options')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(renderer.con, 0, 0, width,
                                                    renderer.screen_height, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tcod.console.Console(width, height)

    # print the header, with auto-wrap
    window.default_fg = tcod.white
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ')' + option_text
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(renderer.screen_width / 2 - width / 2)
    y = int(renderer.screen_height / 2 - height / 2)
    window.blit(renderer.root, x, y, 0, 0, width, height, 1.0, 0.7)

def inventory_menu(header, inventory_width, player, renderer):
    # show a menu with each item of the inventory as an option
    if len(player.inventory.items) == 0:
        options = ['Inventory is empty']
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append('{0} on main hand'.format(item.name))
            elif player.equipment.off_hand == item:
                options.append('{0} on off hand'.format(item.name))
            else:
                options.append(item.name)

    menu(header, options, inventory_width, renderer)

def main_menu(background_image, menu_width, renderer):
    tcod.image_blit_2x(background_image, 0, 0, 0)

    renderer.root.default_fg = tcod.light_yellow
    tcod.console_print_ex(0, renderer.screen_width // 2, renderer.screen_height // 2 - 4,
                tcod.BKGND_NONE, tcod.CENTER, locale.t('story.game_title'))
    tcod.console_print_ex(0, renderer.screen_width // 2, renderer.screen_height // 2 - 2,
                tcod.BKGND_NONE, tcod.CENTER, 'By Me')

    menu('', ['Play a new game', 'Continue last game', 'Quit'], menu_width, renderer)

def message_box(header, width, renderer):
    menu(header, [], width, renderer)

def level_up_menu(header, menu_width, player, renderer):
    options = ['Strength (+1 attack, from {0})'.format(player.fighter.power),
                'Agility (+1 defense, from {0})'.format(player.fighter.defense),
                ]
    menu(header, options, menu_width, renderer)

def character_screen(player, character_screen_width, character_screen_height, renderer):
    window = tcod.console.Console(character_screen_width, character_screen_height)
    window.default_fg = tcod.white

    info_table = [
        'Character Information',
        'Level: {0}'.format(player.level.current_level),
        'Experience: {0}'.format(player.level.current_xp),
        'Experience to next level: {0}'.format(player.level.experience_to_next_level),
        'Attack: {0}'.format(player.fighter.power),
        'Defense: {0}'.format(player.fighter.defense),
        '-'*20,
        'Attributes:',
        str(player.strength),
        str(player.dexterity),
        str(player.constitution),
        str(player.intelligence),
        str(player.wisdom),
        str(player.charisma),
    ]
    for index, text in enumerate(info_table):
        tcod.console_print_rect_ex(window, 0, index, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, text)

    x = renderer.screen_width // 2 - character_screen_width // 2
    y = renderer.screen_height // 2 - character_screen_height // 2
    window.blit(renderer.root, x, y, 0, 0, character_screen_width, character_screen_height, 1.0, 0.7)

def locations_menu(header, menu_width, locations, renderer):
    # show a menu with each location as an entry point
    if len(locations) == 0:
        options = ['There is nothing notably here']
    else:
        options = []

        for location in locations:
            if not location.visited:
                options.append(location.name)
            else:
                options.append('{0} (visited)'.format(location.name))

    menu(header, options, menu_width, renderer)

def exploration_screen(player, screen_width, screen_height, world_map, target_point, renderer):
    x, y = target_point
    tile = world_map.tiles[x][y]
    biom_name = tile.biom.name.lower()

    window = tcod.console.Console(screen_width, screen_height)
    window.default_fg = tcod.white

    info_table = [
        ' '.join((locale.t('world.exploration.title', biom_name.title(), target_point),
                    locale.t('world.exploration.{0}.scouting'.format(biom_name)),
                    locale.t('world.exploration.{0}.landmark.scouting'.format(biom_name)),
                )),
        '-'*40,
    ]

    if not tile.locations:
        world_map.make_locations(tile)

    if len(tile.locations) > 0:
        info_table.append(locale.t('world.exploration.{0}.landmark.exists'.format(biom_name)))
        for location in tile.locations:
            info_table.append(locale.t('world.exploration.{0}.landmark.entry'.format(biom_name), location.name))
    else:
        info_table.append(locale.t('world.exploration.{0}.landmark.not_exists'.format(biom_name)))

    info_table.append('-'*40)
    info_table.append(locale.t('interface.exploration.go_option'))
    info_table.append(locale.t('interface.exploration.stay_option'))

    height = 0
    for text in info_table:
        height += window.print_box(x=0, y=height, width=screen_width, height=screen_height,
                            string=text, fg=tcod.white)

    x = renderer.screen_width // 2 - screen_width // 2
    y = renderer.screen_height // 2 - screen_height // 2
    window.blit(renderer.root, x, y, 0, 0, screen_width, screen_height, 1.0, 0.7)
