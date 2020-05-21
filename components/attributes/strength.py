from components.attributes.attribute import Attribute

class Strength(Attribute):
    def __init__(self, value):
        super().__init__(value)

        self.name = 'strength'
        self.depleted_condition = 'exhausted'
