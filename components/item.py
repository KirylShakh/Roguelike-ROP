from components.component import Component

class Item(Component):
    def __init__(self, use_function=None, **kwargs):
        self.use_function = use_function
        self.function_args = kwargs
