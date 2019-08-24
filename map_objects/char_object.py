from game_vars import color_vars


class Char:
    def __init__(self, char=None, color=None, name=None, base_name=None):
        self.char = char
        self.name = name

        self.color = color
        self.shadow_color = color_vars.mutated_color(color, 0.4)
        self.distant_color = color_vars.mutated_color(color, 0.5)
        self.distant_shadow_color = color_vars.mutated_color(color, 0.8)

        self.base_name = base_name
