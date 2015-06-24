
class FiniteStateMachine:
    def __init__(self, init_state, sentinel):
        self._buffer = []
        self._init_state = init_state

        self.state = init_state
        self._last_state = None
        self.sentinel = sentinel

        self._dbg_line_number = 0
        self._dbg_column_number = 0

    def clear(self):
        self._buffer.clear()
        self.state = self._init_state
        self._last_state = None

    def _tr(self, state):
        self._last_state = self.state
        self.state = state

    def transit(self, ch):
        pass

    def parse(self, iterable):
        for char in iterable:
            if char == '\n':
                self._dbg_line_number += 1
                self._dbg_column_number = 0
            else:
                self._dbg_column_number += 1

            ret = self.transit(char)
            if ret:
                yield ret

        if self.sentinel:
            ret = self.transit(self.sentinel)
            if ret:
                yield ret

    def yield_buffer(self):
        ret = ''.join(self._buffer)
        self._buffer.clear()

        return ret
