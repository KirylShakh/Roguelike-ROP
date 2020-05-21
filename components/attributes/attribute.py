from components.component import Component

class Attribute(Component):
    def __init__(self, value):
        self.base_value = value

        self.tired = 0
        self.damaged = 0

        self.name = 'attribute'
        self.depleted_condition = 'none'

    @property
    def value(self):
        return self.base_value - self.tired - self.damaged

    def tire(self, amount):
        if amount > self.value:
            return False
        self.tired += amount
        return True

    def rest(self, amount):
        self.tired -= amount
        if self.tired < 0:
            self.tired = 0

    def damage(self, amount):
        self.damaged += amount

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
