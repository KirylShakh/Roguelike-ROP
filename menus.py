import tcod

def menu(con, header, options, width, screen_width, screen_height, root):
    if len(options) > 26:
        raise ValueError('Cannot have more than 26 options')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
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
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    window.blit(root, x, y, 0, 0, width, height, 1.0, 0.7)

def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height, root):
    # show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ['Inventory is empty']
    else:
        options = [item.name for item in inventory.items]

    menu(con, header, options, inventory_width, screen_width, screen_height, root)

def main_menu(con, background_image, screen_width, screen_height, root):
    tcod.image_blit_2x(background_image, 0, 0, 0)

    root.default_fg = tcod.light_yellow
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, tcod.BKGND_NONE, tcod.CENTER,
                'Tombs Of The Ancient Kings')
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 2, tcod.BKGND_NONE, tcod.CENTER,
                'By Me')

    menu(con, '', ['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height, root)

def message_box(con, header, width, screen_width, screen_height, root):
    menu(con, header, [], width, screen_height, screen_height, root)

def level_up_menu(con, header, player, menu_width, screen_width, screen_height, root):
    options = ['Constitution (+20 HP, from {0})'.format(player.fighter.max_hp),
                'Strength (+1 attack, from {0})'.format(player.fighter.power),
                'Agility (+1 defense, from {0})'.format(player.fighter.defense),
                ]
    menu(con, header, options, menu_width, screen_width, screen_height, root)

def character_screen(player, character_screen_width, character_screen_height, screen_width, screen_height, root):
    window = tcod.console.Console(character_screen_width, character_screen_height)

    window.default_fg = tcod.white
    tcod.console_print_rect_ex(window, 0, 1, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Character Information')
    tcod.console_print_rect_ex(window, 0, 2, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Level: {0}'.format(player.level.current_level))
    tcod.console_print_rect_ex(window, 0, 3, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Experience: {0}'.format(player.level.current_xp))
    tcod.console_print_rect_ex(window, 0, 4, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Experience to next level: {0}'.format(player.level.experience_to_next_level))
    tcod.console_print_rect_ex(window, 0, 6, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Maximum HP: {0}'.format(player.fighter.max_hp))
    tcod.console_print_rect_ex(window, 0, 7, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Attack: {0}'.format(player.fighter.power))
    tcod.console_print_rect_ex(window, 0, 8, character_screen_width, character_screen_height,
                                tcod.BKGND_NONE, tcod.LEFT, 'Defense: {0}'.format(player.fighter.defense))

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    window.blit(root, x, y, 0, 0, character_screen_width, character_screen_height, 1.0, 0.7)
