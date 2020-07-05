import tcod


player = tcod.white

lightning_arc = tcod.lightest_sky
fireball_explosion = tcod.dark_orange
explosion = tcod.light_orange

forest = tcod.dark_green
forest_bg = tcod.black

dark_wall = tcod.Color(0, 0, 100)
dark_ground = tcod.Color(50, 50, 150)
light_wall = tcod.Color(130, 110, 50)
light_ground = tcod.Color(200, 180, 50)

target_message = tcod.light_cyan
error_message = tcod.red
warning = tcod.yellow
spell = tcod.orange
crit_message = tcod.light_red

soil = tcod.black
wood = tcod.Color(128, 64, 0)
dirt_road = tcod.Color(145, 90, 36)
body = tcod.amber
blood = tcod.dark_red

def mutated_color(color, mult=0.5):
    return tcod.Color(
        color.r - int(color.r * mult),
        color.g - int(color.g * mult),
        color.b - int(color.b * mult)
    )

def mutated_color_detailed(color, mult_r=0, mult_g=0, mult_b=0):
    return tcod.Color(
        min(255, int(color.r * mult_r)),
        min(255, int(color.g * mult_g)),
        min(255, int(color.b * mult_b)),
    )
