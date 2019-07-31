from action_processing.results.result import Result
from game_states import GameStates
from game_messages import Message


class EquipResult(Result):
    def run(self, item):
        player = self.engine.entities.player
        equip_results = player.equipment.toggle_equip(item)

        for equip_result in equip_results:
            equipped = equip_result.get('equipped')
            if equipped:
                self.engine.message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

            dequipped = equip_result.get('dequipped')
            if dequipped:
                self.engine.message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

        self.engine.game_state = GameStates.ENEMY_TURN
