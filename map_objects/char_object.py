from game_vars import color_vars


class Char:
    def __init__(self, char=None, color=None, bg_color=None):
        self.char = char

        self.set_color(color)
        self.set_bg_color(bg_color)

        self.regulatory_flags = set()

    def set_color(self, color):
        self.color = color

        self.shadow_color = color_vars.mutated_color(color, 0.4)
        self.distant_color = color_vars.mutated_color(color, 0.5)
        self.distant_shadow_color = color_vars.mutated_color(color, 0.8)

    def set_bg_color(self, bg_color):
        self.bg_color = bg_color
        self.bg_color_distant = color_vars.mutated_color(bg_color, 0.5)
