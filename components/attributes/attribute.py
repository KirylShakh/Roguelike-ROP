from components.component import Component

class Attribute(Component):
    def __init__(self, value):
        self.base_value = value

        self.tired = 0
        self.damaged = 0

        self.used_in_this_turn = False
        self.turns_since_damaged = 0
        self.regeneration_delay = 5

        self.name = 'attribute'
        self.depleted_condition = 'none'

    @property
    def value(self):
        return self.base_value - self.tired - self.damaged

    @property
    def modifier(self):
        modifier = (self.value // 10) * 2
        if modifier is 0:
            modifier = 1
        return modifier

    def tire(self, amount):
        if amount > self.value:
            return False
        self.tired += amount
        self.used_in_this_turn = True
        return True

    def take_breather(self):
        if not self.used_in_this_turn and self.tired > 0:
            self.rest(self.modifier)

        if self.turns_since_damaged >= self.regeneration_delay and self.damaged > 0:
            self.heal(self.modifier)
        else:
            self.turns_since_damaged += 1

    def rest(self, amount):
        self.tired -= amount
        if self.tired < 0:
            self.tired = 0

    def damage(self, amount):
        self.damaged += amount
        self.used_in_this_turn = True
        self.turns_since_damaged = 0

    def heal(self, amount):
        self.damaged -= amount
        if self.damaged < 0:
            self.damaged = 0

    def depleted(self):
        return self.value <= 0

    def depleted_effect(self):
        return {'condition': None}

    def __str__(self):
        return '{0:13}:{1:2d}/{2:2d}t/{3:2d}d = {4:2d}'.format(self.name.title(), self.base_value, self.tired,
                                                                self.damaged, self.value)
