from components.component import Component

class Equippable(Component):
    def __init__(self, slot=None, power_bonus=0, defense_bonus=0, max_hp_bonus=0, damage_types=None):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

        self.damage_types = damage_types
        if self.damage_types is None:
            self.damage_types = set()
