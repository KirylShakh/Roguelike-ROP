from components.attributes.attribute import Attribute

class Constitution(Attribute):
    def __init__(self, value):
        super().__init__(value)

        self.name = 'constitution'
        self.depleted_condition = 'dead'

    def depleted_effect(self):
        return {'dead': self.owner, 'xp': self.owner.fighter.xp}
