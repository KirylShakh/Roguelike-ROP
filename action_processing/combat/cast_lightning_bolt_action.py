import tcod

from game_messages import Message
from combat.spells.lightning_bolt import LightningBolt
from combat.attacks.cast_scroll import CastScroll

from action_processing.actions.action import Action
from action_processing.animations.lightning_animation import LightningAnimation


class CastLightningBoltAction(Action):
    def run(self, actor, caster_level=None):
        if not caster_level:
            caster_level = actor.caster.level

        spell = LightningBolt(caster_level)
        results = []

        target = None
        closest_distance = spell.maximum_range + 1

        for entity in self.engine.entities.all:
            if entity.fighter and entity != actor and self.engine.fov_map.fov[entity.x][entity.y]:
                distance = actor.distance_to(entity)

                if distance < closest_distance:
                    target = entity
                    closest_distance = distance

        if target:
            attack = CastScroll(actor, target, spell)
            if attack.too_tired_to_execute():
                results.extend(attack.log_too_tired_results())
                return results

            results.append({'consumed': True, 'target': target,
                    'message': Message('A lightning bolt strikes the {0} with a loud thunder'.format(target.name))})

            from_point = (self.engine.entities.player.x, self.engine.entities.player.y)
            animation = LightningAnimation(self.engine, from_point, target, attack=attack)
            self.engine.animations.append(animation)
        else:
            results.append({'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike', tcod.red)})

        return results
