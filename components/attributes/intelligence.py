from components.attributes.attribute import Attribute

class Intelligence(Attribute):
    def __init__(self, value):
        super().__init__(value)

        self.name = 'intelligence'
        self.depleted_condition = 'mad'
