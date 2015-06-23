
class InvalidState(Exception):
    def __init__(self, fsm):
        super(InvalidState, self).__init__(
            'invalid state "%s" at l%s:c%s:ls%s'
            % (fsm.state,
               fsm._dbg_line_number,
               fsm._dbg_column_number,
               fsm._last_state))


class InvalidInput(Exception):
    def __init__(self, ch, fsm):
        super(InvalidInput, self).__init__(
            'invalid input "%s" at l%s:c%s:s%s'
            % (ch,
               fsm._dbg_line_number,
               fsm._dbg_column_number,
               fsm.state))


class PrematureSentinel(Exception):
    def __init__(self, fsm):
        super(PrematureSentinel, self).__init__(
            'premature sentinel reached at s%s:ls%s:b%s'
            % (fsm.state,
               fsm._last_state,
               fsm._buffer)
        )
