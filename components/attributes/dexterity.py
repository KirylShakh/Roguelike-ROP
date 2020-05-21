from components.attributes.attribute import Attribute

class Dexterity(Attribute):
    def __init__(self, value):
        super().__init__(value)

        self.name = 'dexterity'
        self.depleted_condition = 'paralyzed'
