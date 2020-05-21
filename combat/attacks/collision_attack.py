from game_messages import Message


class CollisionAttack:
    def __init__(self, targets, collides_with='something heavy'):
        if isinstance(targets, list):
            self.targets = targets
        else:
            self.targets = [targets]

        self.collision_power = 5
        self.collides_with = collides_with

    def attacked_attribute(self, target):
        return target.constitution

    @property
    def damage_amount(self):
        return self.collision_power

    def resist_damage(self, target):
        return max(self.damage_amount - target.fighter.defense, 0)

    def damage(self, target):
        attacked_attribute = self.attacked_attribute(target)
        if attacked_attribute.depleted():
            return [] 
        damage_amount = self.resist_damage(target)

        attacked_attribute.damage(damage_amount)
        return self.log_damaged_results(target, attacked_attribute, damage_amount)

    def execute(self):
        results = []
        for target in self.targets:
            results.extend(self.damage(target))
        return results

    def log_damaged_results(self, target, attacked_attribute, damage_amount):
        results = []

        if damage_amount > 0:
            results.append({'message': Message(self.harm_message(target, attacked_attribute, damage_amount))})
        else:
            results.append({'message': Message(self.resisted_message(target, attacked_attribute))})

        if attacked_attribute.depleted():
            results.append(attacked_attribute.depleted_effect())

        return results

    def harm_message(self, target, attacked_attribute, damage_amount):
        return '{0} slams into {1} for {2} damage.'.format(target.name.capitalize(),
                    self.collides_with, str(damage_amount))

    def resisted_message(self, target, attacked_attribute):
        return '{0} collides with {1} but stays its ground'.format(target.name.capitalize(),
                    self.collides_with)
