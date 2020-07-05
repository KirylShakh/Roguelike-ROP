import tcod

from components.component import Component
from game_messages import Message
from combat.attacks.base_attack import BaseAttack
from combat.attacks.damage_types import DamageTypes

class Fighter(Component):
    def __init__(self, defense, power, xp=0):
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

        self.unarmed_damage_types = {DamageTypes.BLUDGEONING}

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

    def damage_types(self):
        if self.owner and self.owner.equipment and self.owner.equipment.main_hand:
            return self.owner.equipment.main_hand.equippable.damage_types | self.unarmed_damage_types
        else:
            return self.unarmed_damage_types
