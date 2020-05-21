import tcod

from game_messages import Message
from combat.spells.fireball import Fireball
from combat.attacks.cast_scroll import CastScroll

from action_processing.actions.action import Action
from action_processing.animations.explosion_animation import ExplosionAnimation


class CastFireballAction(Action):
    def run(self, actor, target_point, caster_level=None):
        if not caster_level:
            caster_level = actor.caster.level

        results = []
        target_x, target_y = target_point
        if not self.engine.fov_map.fov[target_x][target_y]:
            results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', tcod.yellow)})
            return results

        spell = Fireball(caster_level)
        targets = []
        for entity in self.engine.entities.all:
                if entity.distance(target_x, target_y) <= spell.radius and entity.fighter:
                    targets.append(entity)

        attack = CastScroll(actor, targets, spell)
        if attack.too_tired_to_execute():
            results.extend(attack.log_too_tired_results())
            return results

        results.append({'consumed': True, 'message': Message('The fireball explodes, burning everything within {0} tiles'.format(spell.radius), tcod.orange)})

        animation = ExplosionAnimation(self.engine, (target_x, target_y), spell.radius, tcod.light_orange, attack)
        self.engine.animations.append(animation)

        return results
