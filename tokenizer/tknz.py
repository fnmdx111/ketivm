from .fsm import FiniteStateMachine
from .exceptions import InvalidState


class MyFSM(FiniteStateMachine):

    NEW_LINE = 'new-line'
    LINE_NUMBER = 'line-number'
    COMMENT = 'comment'
    INSTRUCTION = 'inst'
    IDENTIFIER = 'id'

    def __init__(self):
        super(MyFSM, self).__init__(self.NEW_LINE, '\n')

    def transit(self, ch):
        if self.state == self.COMMENT:
            if ch == '\n':
                self._tr(self.NEW_LINE)
            else:
                pass

        elif self.state == self.NEW_LINE:
            assert not self._buffer
            if ch == '\n':
                pass
            elif ch == ';':
                self._tr(self.COMMENT)
            elif ch.isdigit():
                self._buffer.append(ch)
                self._tr(self.LINE_NUMBER)
            elif ch.isalpha():
                self._buffer.append(ch)
                self._tr(self.INSTRUCTION)

        elif self.state == self.LINE_NUMBER:
            assert self._buffer
            if ch.isdigit():
                self._buffer.append(ch)
            elif ch == '\n':
                self._tr(self.NEW_LINE)
                if self._buffer:
                    return self.LINE_NUMBER, int(self.yield_buffer())
            elif ch.isspace():
                self._tr(self.INSTRUCTION)
                if self._buffer:
                    return self.LINE_NUMBER, int(self.yield_buffer())

        elif self.state == self.INSTRUCTION:
            if ch == '-':
                self._buffer.append(ch)
            elif ch.isalpha():
                self._buffer.append(ch)
            elif ch == '\n':
                self._tr(self.NEW_LINE)
                if self._buffer:
                    return self.INSTRUCTION, self.yield_buffer()
            elif ch.isspace():
                self._tr(self.IDENTIFIER)
                if self._buffer:
                    return self.INSTRUCTION, self.yield_buffer()

        elif self.state == self.IDENTIFIER:
            if ch == ',':
                if self._buffer:
                    return self.IDENTIFIER, self.yield_buffer()
            elif ch == '\n':
                self._tr(self.NEW_LINE)
                if self._buffer:
                    return self.IDENTIFIER, self.yield_buffer()
            elif ch.isspace():
                if self._buffer:
                    return self.IDENTIFIER, self.yield_buffer()
            else:
                self._buffer.append(ch)

        else:
            raise InvalidState(self)
