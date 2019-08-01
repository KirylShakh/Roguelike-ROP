from action_processing.actions.action import Action
from game_states import GameStates


class AnimateAction(Action):
    def run(self):
        while len(self.engine.animations) != 0:
            completed = []
            for animation in self.engine.animations:
                animation.next_tick()
                if animation.completed:
                    completed.append(animation)

            for animation in completed:
                self.engine.animations.remove(animation)

            self.engine.render_tick()

        self.engine.game_state = GameStates.PLAYERS_TURN
