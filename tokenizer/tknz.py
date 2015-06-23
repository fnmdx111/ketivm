import string
from .fsm import FiniteStateMachine, InvalidState


class MyFSM(FiniteStateMachine):

    NEW_LINE = 'new-line'
    LINE_NUMBER = 'line-number'
    COMMENT = 'comment'
    INSTRUCTION = 'inst'
    IDENTIFIER = 'id'

    def transit(self, ch):
        if self.state == self.COMMENT:
            if ch == '\n':
                self.state = self.NEW_LINE
            else:
                pass

        elif self.state == self.NEW_LINE:
            assert not self._buffer
            if ch == '\n':
                pass
            elif ch == ';':
                self.state = self.COMMENT
            elif ch in string.digits:
                self._buffer.append(ch)
                self.state = self.LINE_NUMBER
            elif ch in string.ascii_letters:
                self._buffer.append(ch)
                self.state = self.INSTRUCTION

        elif self.state == self.LINE_NUMBER:
            assert self._buffer
            if ch in string.digits:
                self._buffer.append(ch)
            elif ch == '\n':
                self.state = self.NEW_LINE
                if self._buffer:
                    return self.LINE_NUMBER, int(self.yield_buffer())
            elif ch in string.whitespace:
                self.state = self.INSTRUCTION
                if self._buffer:
                    return self.LINE_NUMBER, int(self.yield_buffer())

        elif self.state == self.INSTRUCTION:
            if ch == '-':
                self._buffer.append(ch)
            elif ch in string.ascii_letters:
                self._buffer.append(ch)
            elif ch == '\n':
                self.state = self.NEW_LINE
                if self._buffer:
                    return self.INSTRUCTION, self.yield_buffer()
            elif ch in string.whitespace:
                self.state = self.IDENTIFIER
                if self._buffer:
                    return self.INSTRUCTION, self.yield_buffer()

        elif self.state == self.IDENTIFIER:
            if ch == ',':
                if self._buffer:
                    return self.IDENTIFIER, self.yield_buffer()
            elif ch == '\n':
                self.state = self.NEW_LINE
                if self._buffer:
                    return self.IDENTIFIER, self.yield_buffer()
            elif ch in string.whitespace:
                if self._buffer:
                    return self.IDENTIFIER, self.yield_buffer()
            else:
                self._buffer.append(ch)

        else:
            raise InvalidState()
