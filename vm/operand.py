from ast import literal_eval
import re
from numbers import Number
from .exceptions import InvalidMacro

T_STK_DATA_REF = 'type-data-stack-reference'
T_MACRO_CALL = 'type-macro-call'
T_CONSTANT = 'type-constant'

OP_TOP = 'top'
OP_BOTTOM = 'bottom'
OP_POP = 'pop'
OP_RRD = 'rrd'

IND_REFERENCING = '@'
IND_MACRO_CALL = '#'


def _macro_rrd(vm):
    vm._reg_read = input()
    return vm._reg_read


def _macro_invalid_macro(name):
    def _macro(vm):
        raise InvalidMacro(name, vm)
    return _macro


MACRO_TABLE = {
    OP_POP: lambda vm: vm._stk_data.pop(),
    OP_RRD: _macro_rrd,
}

class Operand:

    PAT_OPER_1 = re.compile(r'(@|#|!)?([a-zA-Z0-9_-]+)(?:\(([0-9]+)\))?')
    PAT_OPER_STR1 = re.compile(r"'(.*)'")
    PAT_OPER_STR2 = re.compile(r'"(.*)"')


    """
    Standard operands, such as @top, @top(2), #ptop, LOOP, LB-EQ, are
    used in statements in Keti VL.
    """

    def __init__(self, ref, vm=None):
        self.vm = vm

        indicator = ''
        content = ''
        param = 0

        if isinstance(ref, str):
            if ref.startswith("'"):
                ret = Operand.PAT_OPER_STR1.findall(ref)
                if len(ret) == 1:
                    content = ret[0]
            elif ref.startswith('"'):
                ret = Operand.PAT_OPER_STR2.findall(ref)
                if len(ret) == 1:
                    content = ret[0]
            else:
                if ref[0].isdigit():
                    content = literal_eval(ref)
                else:
                    ret = Operand.PAT_OPER_1.findall(ref)
                    if ret and len(ret[0]) == 3:
                        indicator, content, param = ret[0]
                        # '@' stands for referencing, '#' stands for macro call

            self.indicator = indicator
            self.content = content
            self.param = param

            if not param:
                param = 0
            else:
                param = int(param)
        elif isinstance(ref, Number):
            self.content = ref

        self._type = T_CONSTANT
        if indicator == IND_REFERENCING:
            self._type = T_STK_DATA_REF
        elif indicator == IND_MACRO_CALL:
            self._type = T_MACRO_CALL
            self._macro = MACRO_TABLE.get(content,
                                          _macro_invalid_macro(content))
            # TODO add debug information, like macro name, ip-then etc.

        if content == OP_TOP:
            self._pointer = -param - 1
        elif content == OP_BOTTOM:
            self._pointer = param
        elif content == OP_POP:
            self._pointer = 0
        elif content == OP_RRD:
            self._pointer = OP_RRD

    def __call__(self, vm=None):
        ctx = vm or self.vm
        if self._type == T_STK_DATA_REF:
            return vm._stk_data[self._pointer]
        elif self._type == T_MACRO_CALL:
            return self._macro(ctx)
        elif self._type == T_CONSTANT:
            return self.content

    def __str__(self):
        return 'OP %s%s%s' % (self.indicator,
                                 self.content,
                                 '(%s)' % self.param if self.param
                                 else '')

    def __repr__(self):
        return str(self)
