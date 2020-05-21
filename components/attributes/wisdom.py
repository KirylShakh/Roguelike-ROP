from components.attributes.attribute import Attribute

class Wisdom(Attribute):
    def __init__(self, value):
        super().__init__(value)

        self.name = 'wisdom'
        self.depleted_condition = 'terrified'
