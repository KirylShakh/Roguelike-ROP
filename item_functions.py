import tcod

from game_messages import Message

from action_processing.combat.cast_fireball_action import CastFireballAction
from action_processing.combat.cast_lightning_bolt_action import CastLightningBoltAction
from action_processing.combat.cast_confuse_action import CastConfuseAction
from action_processing.combat.cast_heal_action import CastHealAction


def heal(*args, **kwargs):
    caster = args[0]
    caster_level = kwargs.get('caster_level')
    engine = kwargs.get('engine')

    action = CastHealAction(engine)
    return action.run(caster, caster_level)

def cast_lightning(*args, **kwargs):
    caster = args[0]
    caster_level = kwargs.get('caster_level')
    engine = kwargs.get('engine')

    action = CastLightningBoltAction(engine)
    return action.run(caster, caster_level)

def cast_fireball(*args, **kwargs):
    caster = args[0]
    caster_level = kwargs.get('caster_level')
    engine = kwargs.get('engine')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    action = CastFireballAction(engine)
    return action.run(caster, (target_x, target_y), caster_level)

def cast_confuse(*args, **kwargs):
    caster = args[0]
    caster_level = kwargs.get('caster_level')
    engine = kwargs.get('engine')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    action = CastConfuseAction(engine)
    return action.run(caster, (target_x, target_y), caster_level)
