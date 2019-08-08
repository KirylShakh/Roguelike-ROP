import tcod

from game_messages import Message
from components.ai import ConfusedMonster

from action_processing.animations.push_animation import PushAnimation
from action_processing.animations.lightning_animation import LightningAnimation
from action_processing.animations.explosion_animation import ExplosionAnimation
from action_processing.actions.take_damage_action import TakeDamageAction

def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', tcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better', tcod.green)})

    return results

def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    engine = kwargs.get('engine')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities.all:
        if entity.fighter and entity != caster and fov_map.fov[entity.x][entity.y]:
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target,
                'message': Message('A lightning bolt strikes the {0} with a loud thunder for {1} damage'.format(target.name, damage))})

        action = TakeDamageAction(engine)
        action.setup(target, damage)

        from_point = (engine.entities.player.x, engine.entities.player.y)
        animation = LightningAnimation(engine, from_point, target, callback_action=action)
        engine.animations.append(animation)
    else:
        results.append({'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike', tcod.red)})

    return results

def cast_fireball(*args, **kwargs):
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    engine = kwargs.get('engine')

    results = []

    if not fov_map.fov[target_x][target_y]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', tcod.yellow)})
        return results

    results.append({'consumed': True, 'message': Message('The fireball explodes, burning everything within {0} tiles'.format(radius), tcod.orange)})

    animation = ExplosionAnimation(engine, (target_x, target_y), radius, tcod.light_orange, damage)
    engine.animations.append(animation)

    return results

def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not fov_map.fov[target_x][target_y]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', tcod.yellow)})
        return results

    for entity in entities.all:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)
            confused_ai.own(entity)
            entity.ai = confused_ai

            results.append({'consumed': True, 'message': Message('The eyes of the {0} look vacant, as he starts to stumble around'.format(entity.name), tcod.light_green)})
            break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location', tcod.yellow)})

    return results
