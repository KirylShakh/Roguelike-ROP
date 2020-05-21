import tcod

from components.component import Component
from game_messages import Message
from combat.attacks.base_attack import BaseAttack

class Fighter(Component):
    def __init__(self, defense, power, xp=0):
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus

    def attack(self, target):
        attack_command = BaseAttack(self.owner, target)
        return attack_command.execute()
