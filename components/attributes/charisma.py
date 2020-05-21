from components.attributes.attribute import Attribute

class Charisma(Attribute):
    def __init__(self, value):
        super().__init__(value)

        self.name = 'charisma'
        self.depleted_condition = 'monster'
