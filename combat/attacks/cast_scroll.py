from game_messages import Message
from combat.attacks.base_attack import BaseAttack


class CastScroll(BaseAttack):
    def __init__(self, attacker, targets, spell):
        super().__init__(attacker, targets)

        self.spell = spell

    @property
    def attacking_attribute(self):
        return self.attacker.intelligence # for scrolls its always intelligence # self.attacker.attribute_by_name(self.spell.cast_attribute)

    def attacked_attribute(self, target):
        return target.attribute_by_name(self.spell.damage_attribute)

    @property
    def damage_amount(self):
        return self.spell.damage

    @property
    def tire_amount(self):
        return self.spell.tire_cost

    def resist_damage(self, target):
        return self.damage_amount

    def apply_status(self, target, attacked_attribute, damage_amount):
        return self.spell.apply_status(target)

    def harm_message(self, target, attacked_attribute, damage_amount):
        return '{0} casts scroll of {4} on {1} {3} for {2} damage.'.format(self.attacker.name.capitalize(),
                    target.name, str(damage_amount), attacked_attribute.name, self.spell.name)

    def resisted_message(self, target, attacked_attribute):
        return '{0} casts scroll of {4} on {1} {2} but spell fails to do any harm.'.format(self.attacker.name.capitalize(),
                    target.name, attacked_attribute, self.spell.name)

    def too_tired_message(self):
        return '{0} mind is too tired to cast scroll of {1}.'.format(self.attacker.name.capitalize(),
                    self.spell.name)
