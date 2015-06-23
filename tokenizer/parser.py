from ast import literal_eval
from .tknz import MyFSM
from itertools import chain
from .fsm import FiniteStateMachine
from .exceptions import InvalidInput, PrematureSentinel
from spec.identifiers import *
from vm.operand import Operand


class IdentifierFSM(FiniteStateMachine):

    INIT = 'init'
    MACRO = 'macro'
    NUM_LITERAL = 'num-literal'
    VAL = 'val'
    VAL_PARAM = 'val-param'
    REF = 'ref'
    SQ_STR = 'sq-str'
    DQ_STR = 'dq-str'
    LABEL = 'label'
    FIN = 'fin'

    TYPE = 'type'
    PAYLOAD = 'payload'
    PARAM = 'param'

    def __init__(self):
        super(IdentifierFSM, self).__init__(self.INIT, 'sentinel')

    def transit(self, ch):
        if self.state == self.INIT:
            if ch == IND_MACRO:
                self._tr(self.MACRO)
                return self.TYPE, T_MACRO
            elif ch == ':':
                self._tr(self.LABEL)
                self._buffer.append(ch)
                return self.TYPE, T_CONSTANT
            elif ch == IND_VAL:
                self._tr(self.VAL)
                return self.TYPE, T_VAL
            elif ch == "'":
                self._tr(self.SQ_STR)
                self._buffer.append(ch)
                return self.TYPE, T_CONSTANT
            elif ch == '"':
                self._tr(self.DQ_STR)
                self._buffer.append(ch)
                return self.TYPE, T_CONSTANT
            elif ch.isdigit():
                self._tr(self.NUM_LITERAL)
                self._buffer.append(ch)
                return self.TYPE, T_CONSTANT
            elif ch.isalpha():
                self._tr(self.REF)
                self._buffer.append(ch)
                return self.TYPE, T_REF

        elif self.state == self.MACRO:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, self.yield_buffer()
            elif ch == '(':
                raise InvalidInput(ch, self)
            else:
                self._buffer.append(ch)

        elif self.state == self.LABEL:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, self.yield_buffer()
            else:
                self._buffer.append(ch)

        elif self.state == self.NUM_LITERAL:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, literal_eval(self.yield_buffer())
            else:
                self._buffer.append(ch)

        elif self.state == self.VAL:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, self.yield_buffer()
                # no param is attached to this VAL
            elif ch == '(':
                self._tr(self.VAL_PARAM)
                return self.PAYLOAD, self.yield_buffer()
            else:
                self._buffer.append(ch)

        elif self.state == self.VAL_PARAM:
            if ch == ')':
                self._tr(self.FIN)
                return self.PARAM, literal_eval(self.yield_buffer())
            elif ch == self.sentinel:
                raise PrematureSentinel(self)
            else:
                self._buffer.append(ch)

        elif self.state == self.REF:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, self.yield_buffer()
            else:
                self._buffer.append(ch)

        elif self.state == self.SQ_STR:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, literal_eval(self.yield_buffer())
            else:
                self._buffer.append(ch)

        elif self.state == self.DQ_STR:
            if ch == self.sentinel:
                self._tr(self.FIN)
                return self.PAYLOAD, literal_eval(self.yield_buffer())
            else:
                self._buffer.append(ch)

    @staticmethod
    def is_advanced_operand(token):
        if isinstance(token, str):
            if token.startswith(IND_MACRO):
                return True
            elif token.startswith(IND_VAL):
                return True

        return False


def make_operand(op_token):
    id_fsm = IdentifierFSM()

    op_type = None
    op_payload = None
    op_param = None

    for type_, token in id_fsm.tokens_of(op_token):
        if type_ == IdentifierFSM.TYPE:
            op_type = token
        elif type_ == IdentifierFSM.PAYLOAD:
            op_payload = token
        elif type_ == IdentifierFSM.PARAM:
            if IdentifierFSM.is_advanced_operand(token):
                op_param = make_operand(token)
            else:
                op_param = token

    assert op_type and op_payload is not None

    return Operand(op_type, op_payload, op_param)


def parse(fp):
    my_fsm = MyFSM()

    stmt = []
    tokens = my_fsm.tokens_of(chain.from_iterable(fp))

    for type_, token in tokens:
        if type_ == MyFSM.INSTRUCTION:
            stmt.append([token, []])
        elif type_ == MyFSM.IDENTIFIER:
            op = make_operand(token)
            stmt[-1][-1].append(op)

    return stmt
