from action_processing.actions.action import Action


class LevelUpAction(Action):
    def run(self, level_up):
        player = self.engine.entities.player
        if level_up == 'hp':
            player.fighter.base_max_hp += 20
            player.fighter.heal(20)
        elif level_up == 'str':
            player.fighter.base_power += 1
        elif level_up == 'def':
            player.fighter.base_defense += 1

        self.engine.game_state = self.engine.previous_game_state
