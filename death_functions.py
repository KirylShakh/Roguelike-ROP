import tcod

from game_states import GameStates
from renderer_object import RenderOrder
from game_messages import Message

def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return Message('You died', color=tcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = Message('{0} is dead'.format(monster.name.capitalize()), color=tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of {0}'.format(monster.name)
    monster.render_order = RenderOrder.CORPSE

    return death_message
