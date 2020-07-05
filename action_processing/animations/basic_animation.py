class BasicAnimation(object):
    def __init__(self, engine):
        self.engine = engine
        self.regulatory_flags = set()
        self.completed = False

    def next_tick(self):
        return self.complete()

    def complete(self):
        self.completed = True
        return []

    def stop(self):
        return self.complete()
