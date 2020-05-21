import tcod

from game_messages import Message
from combat.spells.heal import Heal
from combat.attacks.drink_potion import DrinkPotion

from action_processing.actions.action import Action


class CastHealAction(Action):
    def run(self, actor, caster_level=None):
        if not caster_level:
            caster_level = actor.caster.level

        results = []

        attack = DrinkPotion(actor, Heal(caster_level))
        results.extend(attack.execute())

        results.append({'consumed': True})

        return results
