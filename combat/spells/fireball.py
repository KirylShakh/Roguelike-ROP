from random import randint

from combat.spells.spell import Spell, SpellTags

class Fireball(Spell):
    def setup(self):
        self.name = 'fireball'
        self.level = 3
        self.value_die = 4
        self.radius = 3

        self.tags.extend([SpellTags.DAMAGE, SpellTags.ELEMENTAL, SpellTags.FIRE])

        self.cast_attribute = 'intelligence'
        self.damage_attribute = 'constitution'

        self.caster_level = min(self.level + 4, self.caster_level) # for now spell cannot be scaled more than 4 levels above
        self.damage = self.inflicted_value()

    def harm_message(self, target):
        return 'The {0} gets burned for {1} damage'.format(target.name, self.damage)
