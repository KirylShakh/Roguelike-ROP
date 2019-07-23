import tcod

from game_states import GameStates
from renderer_object import RenderOrder

def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return 'You died', GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = '{0} is dead'.format(monster.name.capitalize())

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of {0}'.format(monster.name)
    monster.render_order = RenderOrder.CORPSE

    return death_message
