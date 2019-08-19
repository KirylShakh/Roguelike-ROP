import tcod


player = tcod.white

greenskin = tcod.desaturated_green
troll = tcod.darker_green

dagger = tcod.sky
sword = tcod.sky
shield = tcod.darker_orange
healing_potion = tcod.violet

fireball_scroll = tcod.red
lightning_scroll = tcod.yellow
confuse_scroll = tcod.light_pink

lightning_arc = tcod.lightest_sky
fireball_explosion = tcod.dark_orange

target_message = tcod.light_cyan

forest = tcod.dark_green
forest_bg = tcod.black

dark_wall = tcod.Color(0, 0, 100)
dark_ground = tcod.Color(50, 50, 150)
light_wall = tcod.Color(130, 110, 50)
light_ground = tcod.Color(200, 180, 50)

warning = tcod.yellow
spell = tcod.orange

soil = tcod.black

tree_choices = {
    'brown': 50, # alder, elm
    'yellow': 40, # pine
    'white': 20, # birch
    'light_grey': 15, # aspen, oak, alder, elm
    'dark_grey': 5, # acacia
    'red': 5, # willow
    'darkest_grey': 5, # bird cherry
    'green': 5, # lemon
}

tree_choices_colors = {
    'white': tcod.Color(147, 137, 128), # birch
    'light_grey': tcod.Color(100, 100, 100), # aspen, oak, alder, elm
    'dark_grey': tcod.Color(79, 78, 68), # acacia
    'brown': tcod.Color(40, 28, 4), # alder, elm
    'darkest_grey': tcod.Color(64, 58, 40), # bird cherry
    'yellow': tcod.Color(80, 50, 5), # pine
    'red': tcod.Color(71, 28, 7), # willow
    'green': tcod.Color(64, 89, 20), # lemon
}
tree_choices_names = {
    'white': 'Betula',
    'light_grey': 'Alnus',
    'dark_grey': 'Acacia',
    'brown': 'Ulmus',
    'darkest_grey': 'Prunus',
    'yellow': 'Sequoia',
    'red': 'Salix',
    'green': 'Citrus',
}

grass_choices = {
    'lighter': 25,
    'lightest': 25,
    'darker': 25,
    'darkest': 25,
    'golden': 10,
    'flower_red': 2,
    'flower_violet': 2,
    'flower_white': 2,
    'flower_yellow': 2,
}
grass_choices_colors = {
    'lighter': tcod.Color(101, 219, 98),
    'lightest': tcod.Color(87, 237, 80),
    'darker': tcod.Color(31, 202, 21),
    'darkest': tcod.Color(27, 176, 19),
    'golden': tcod.Color(236, 236, 0),
    'flower_red': tcod.Color(219, 30, 2),
    'flower_violet': tcod.Color(238, 130, 238),
    'flower_white': tcod.Color(238, 238, 238),
    'flower_yellow': tcod.Color(238, 238, 88),
}

def mutated_color(color, mult=0.5):
    return tcod.Color(
        color.r  - int(color.r * mult),
        color.g - int(color.g * mult),
        color.b - int(color.b * mult)
    )
