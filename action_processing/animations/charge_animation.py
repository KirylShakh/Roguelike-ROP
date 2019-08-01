class ChargeAnimation:
    def __init__(self, entity, path):
        self.entity = entity
        self.path = path

        self.path_index = 0

    def next_tick(self):
        if self.path_index >= len(self.path) or self.completed:
            return False

        x, y = self.path[self.path_index]
        self.entity.x = x
        self.entity.y = y

        self.path_index += 1

        return True

    @property
    def completed(self):
        x, y = self.path[-1]
        return self.entity.x == x and self.entity.y == y
