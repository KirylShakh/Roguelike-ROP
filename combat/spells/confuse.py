import tcod

from random import randint

from game_messages import Message
from components.ai import ConfusedMonster
from combat.spells.spell import Spell, SpellTags


class Confuse(Spell):
    def setup(self):
        self.name = 'confuse'
        self.level = 4
        self.value_die = 4

        self.tags |= {SpellTags.DAMAGE, SpellTags.MIND, SpellTags.TARGET}

        self.cast_attribute = 'intelligence'
        self.damage_attribute = 'intelligence'

        self.caster_level = min(self.level + 4, self.caster_level) # for now spell cannot be scaled more than 4 levels above
        self.damage = self.inflicted_value()

    def inflicted_value(self):
        return randint(1, self.value_die)

    @property
    def resist_by(self):
        return None

    def apply_status(self, target):
        confused_ai = ConfusedMonster(target.ai, self.caster_level * 2)
        confused_ai.own(target)
        target.ai = confused_ai

        return [{'message': Message(self.status_message(target), tcod.light_green)}]

    def harm_message(self, target):
        return 'The {0} intelligence got damaged by confusion for {1}'.format(target.name, self.damage)

    def status_message(self, target):
        return 'The eyes of the {0} look vacant, as he starts to stumble around'.format(target.name)
