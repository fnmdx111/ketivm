
class FiniteStateMachine:
    def __init__(self, init_state):
        self._buffer = []
        self.state = init_state

    def transit(self, ch):
        pass

    def tokens_of(self, in_str):
        for char in iter(in_str):
            ret = self.transit(char)
            if ret:
                yield ret

    def yield_buffer(self):
        ret = ''.join(self._buffer)
        self._buffer.clear()

        return ret

class InvalidState(Exception):
    pass

