from components.component import Component

class Tree(Component):
    def __init__(self, diameter=1):
        self.diameter = diameter
        self.tiles = [[]]

    def set_trunk(self, trunk):
        self.trunk = trunk
        self.owner.x, self.owner.y = trunk.center()
