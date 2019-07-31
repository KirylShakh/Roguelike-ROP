import tcod

from action_processing.actions.action import Action


class FullscreenAction(Action):
    def run(self):
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
