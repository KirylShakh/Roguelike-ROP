from components.component import Component

class Item(Component):
    def __init__(self, action=None, targeting=False, targeting_message=None, **kwargs):
        self.action_class = action
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.action_args = kwargs
