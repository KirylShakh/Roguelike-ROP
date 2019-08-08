import time

from action_processing.actions.action import Action
from game_states import GameStates


class AnimateAction(Action):
    def run(self):
        results = []

        while len(self.engine.animations) != 0:
            completed = []
            for animation in self.engine.animations:
                results.extend(animation.next_tick())
                if animation.completed:
                    completed.append(animation)

            for animation in completed:
                self.engine.animations.remove(animation)

            self.engine.render_tick()
            time.sleep(0.15)

        self.engine.game_state = self.engine.previous_game_state

        return results
