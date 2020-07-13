from game_vars import color_vars


class Tile:
    def __init__(self, blocked=False, block_sight = None, bg_color = color_vars.default_bg):
        self.bg_color_base = bg_color
        self.regulatory_flags = set()

        if blocked:
            self.regulatory_flags.add('blocked')

        if (block_sight is None and blocked) or block_sight:
            self.regulatory_flags.add('block_sight')

        self.clear_static_entities()

    def place_static_entity(self, static_entity):
        self.static_entities.append(static_entity)
        self.static_entities_changed()

    def remove_static_entity(self, static_entity):
        if static_entity in self.static_entities:
            self.static_entities.remove(static_entity)
            self.static_entities_changed()

    def clear_static_entities(self):
        self.static_entities = []
        self.top_char_object = None
        self.top_bg_color = self.bg_color_base

    def static_entities_changed(self):
        self.top_bg_color = self.bg_color_base

        if not self.static_entities:
            self.top_char_object = None
            return

        render_order_sorted_entities = sorted(self.static_entities, key=lambda x: x.render_order.value, reverse=True)
        self.top_char_object = render_order_sorted_entities[0].char

        for entity in render_order_sorted_entities:
            if entity.char.bg_color and 'bg_color_stacks' not in entity.char.regulatory_flags:
                self.top_bg_color = entity.char.bg_color
                return

    def set_bg_color(self, color):
        self.bg_color_base = color
        self.static_entities_changed()

    def bg_color(self):
        stacking_bg_colors = [entity.char.bg_color for entity in self.static_entities
                        if entity.char.bg_color and 'bg_color_stacks' in entity.char.regulatory_flags]
        if stacking_bg_colors:
            stacked_bg_color = color_vars.average_color(*stacking_bg_colors)
            return color_vars.average_color(self.top_bg_color, stacked_bg_color)
        else:
            return self.top_bg_color

    def bg_color_distant(self):
        stacking_bg_colors = [entity.char.bg_color for entity in self.static_entities
                        if entity.char.bg_color and 'bg_color_stacks' in entity.char.regulatory_flags]
        if stacking_bg_colors:
            stacked_bg_color = color_vars.average_color(*stacking_bg_colors)
            return color_vars.mutated_color(color_vars.average_color(self.top_bg_color, stacked_bg_color))
        else:
            return color_vars.mutated_color(self.top_bg_color)

    def whats_there(self):
        names = []
        for entity in self.static_entities:
            names.append(entity.name)
        return names

    def unblock(self):
        self.regulatory_flags.discard('blocked')
        self.regulatory_flags.discard('block_sight')

    def block(self):
        self.regulatory_flags.add('blocked')
        self.regulatory_flags.add('block_sight')
