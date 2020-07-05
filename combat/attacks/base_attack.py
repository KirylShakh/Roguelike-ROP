from game_messages import Message
from combat.attacks.damage_types import DamageTypes


class BaseAttack:
    def __init__(self, attacker, targets):
        self.attacker = attacker

        if isinstance(targets, list):
            self.targets = targets
        else:
            self.targets = [targets]

    @property
    def attacking_attribute(self):
        return self.attacker.strength

    def attacked_attribute(self, target):
        return target.constitution

    @property
    def damage_amount(self):
        return self.attacker.fighter.power + self.attacking_attribute.modifier

    @property
    def tire_amount(self):
        return self.attacking_attribute.modifier or 1 # minimal cost of attack is 1

    # apply resists to damage if any and return actual value that should be applied as damage
    def resist_damage(self, target):
        return max(self.damage_amount - target.fighter.defense, 0)

    def apply_status(self, target, attacked_attribute, damage_amount):
        if attacked_attribute.name == 'constitution' and damage_amount >= (attacked_attribute.value + damage_amount) // 2:
            result = {'heavy_damage_attack': True}
            weapon_types = self.attacker.fighter.damage_types()
            if DamageTypes.SLASHING in weapon_types:
                result['chop_attack'] = True
            return [result]
        return []

    # main method for applying damage and status effects to the target.normally should not be overriden
    def damage(self, target):
        attacked_attribute = self.attacked_attribute(target)
        damage_amount = self.resist_damage(target)

        attacked_attribute.damage(damage_amount)
        results = self.apply_status(target, attacked_attribute, damage_amount)

        results.extend(self.log_damaged_results(target, attacked_attribute, damage_amount))
        return results

    def too_tired_to_execute(self):
        return self.tire_amount > self.attacking_attribute.value

    def execute(self):
        if self.attacking_attribute.tire(self.tire_amount):
            results = []
            for target in self.targets:
                results.extend(self.damage(target))
            return results
        else:
            return self.log_too_tired_results()

    def log_damaged_results(self, target, attacked_attribute, damage_amount):
        results = []

        if damage_amount > 0:
            results.append({'message': Message(self.harm_message(target, attacked_attribute, damage_amount))})
        else:
            results.append({'message': Message(self.resisted_message(target, attacked_attribute))})

        if attacked_attribute.depleted():
            results.append(attacked_attribute.depleted_effect())

        results.append({'message': Message(self.tire_message())})

        return results

    def log_too_tired_results(self):
        return [{'too_tired': True}, {'message': Message(self.too_tired_message())}]

    def harm_message(self, target, attacked_attribute, damage_amount):
        weapon = 'unarmed strike'
        if self.attacker.equipment and self.attacker.equipment.main_hand:
            weapon = self.attacker.equipment.main_hand.name

        return '{0} attacks {1} {3} with {4} for {2} damage.'.format(self.attacker.name.capitalize(),
                    target.name, str(damage_amount), attacked_attribute.name, weapon)

    def resisted_message(self, target, attacked_attribute):
        return '{0} attacks {1} {2} but does no damage.'.format(self.attacker.name.capitalize(),
                    target.name, attacked_attribute)

    def tire_message(self):
        return '{0} {1} is tired by {2}'.format(self.attacker.name.capitalize(),
                    self.attacking_attribute.name, str(self.tire_amount))

    def too_tired_message(self):
        return '{0} {1} is too tired to attack'.format(self.attacker.name.capitalize(), self.attacking_attribute.name)
