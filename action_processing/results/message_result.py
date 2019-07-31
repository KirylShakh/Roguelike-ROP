from action_processing.results.result import Result


class MessageResult(Result):
    def run(self, message):
        self.engine.message_log.add_message(message)
