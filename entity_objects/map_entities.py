class MapEntities:
    def __init__(self, player, entities_list=None):
        self.player = player

        if entities_list == None:
            entities_list = []
        self.list = entities_list

        self.list.append(player)

    def append(self, entity):
        self.list.append(entity)

    def remove(self, entity):
        self.list.remove(entity)

    @property
    def all(self):
        return self.list

    def on_turn_start(self):
        for entity in self.all:
            entity.on_turn_start()

    def on_turn_end(self):
        for entity in self.all:
            entity.on_turn_end()

    def find_by_point(self, x, y):
        for entity in self.list:
            if entity.x == x and entity.y == y:
                return entity
        return None

    def get_blocking_at_location(self, x, y):
        for entity in self.list:
            if entity.blocks and entity.x == x and entity.y == y:
                return entity
        return None
