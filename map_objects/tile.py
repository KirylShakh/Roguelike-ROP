class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

        self.explored = False
        self.indoor = False
        self.cultivated = False

        self.char = None

    def unblock(self):
        self.blocked = False
        self.block_sight = False

    def block(self):
        self.blocked = True
        self.block_sight = True
