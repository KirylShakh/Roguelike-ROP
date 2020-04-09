from map_objects.landmarks.landmark import Landmark


class LandmarkArea(Landmark):
    def __init__(self, name):
        super().__init__(name)

        self.landmark_objects = {}

    def init_constants(self):
        super().init_constants()

        self.min_width = 20
        self.max_width = 30

        self.min_height = 15
        self.max_height = 30

    def create_on(self, game_map):
        super().create_on(game_map)

        self.make_landmark_objects()
        for obj in self.landmark_objects.values():
            obj.create_on(game_map)

    def make_landmark_object(self, key, builder_method):
        new_obj = builder_method()

        max_tries = 10
        tries = 1
        while True:
            intersect = False
            for obj in self.landmark_objects.values():
                if new_obj.rect.intersect(obj.rect):
                    intersect = True
                    break
            if not intersect:
                self.landmark_objects[key] = new_obj
                break

            new_obj = builder_method()
            tries += 1
            if tries >= max_tries:
                break

    def make_landmark_objects(self):
        pass

    def blocked(self, tile):
        x, y = tile
        for obj in self.landmark_objects.values():
            if obj.rect.belongs(x, y):
                return True
        return False
