from spec.identifiers import *
from .exceptions import InvalidMacro

OP_TOP = 'top'
OP_BOTTOM = 'bottom'
OP_POP = 'pop'
OP_READ = 'read'
OP_READ_INT = 'read-int'
OP_TEST = 'test'


def _macro_rrd(vm):
    vm._reg_read = input()
    return vm._reg_read

def _macro_pop(vm):
    vm._reg_pop = vm._stk_data.pop()
    return vm._reg_pop

def _macro_read_int(vm):
    vm._reg_read = int(input())
    return vm._reg_read


def _macro_invalid_macro(name):
    def _macro(vm):
        raise InvalidMacro(name, vm)
    return _macro


MACRO_TABLE = {
    OP_POP: _macro_pop,
    OP_READ: _macro_rrd,
    OP_READ_INT: _macro_read_int,
}

class Operand:

    """
    Standard operands, such as @top, @top(2), #ptop, LOOP, LB-EQ, are
    used in statements in Keti VL.
    """

    REF_REG = 'ref-reg'
    REF_IDX = 'ref-rel'

    def __init__(self, type_, payload, param, vm=None):
        self.vm = vm
        self.type_ = type_
        self.payload = payload
        self.param = param

        if type_ == T_MACRO:
            assert not param
            self._macro = MACRO_TABLE.get(payload,
                                          _macro_invalid_macro(payload))

    def __call__(self, vm=None):
        ctx = vm or self.vm

        if self.type_ == T_CONSTANT:
            return self.payload
        elif self.type_ == T_MACRO:
            return self._macro(ctx)
        else:
            if self.param:
                # param is default to None, which in this context equals zero
                p = self.param(ctx) if isinstance(self.param, Operand)\
                    else self.param
            else:
                p = 0

            pointer = -1
            if self.payload == OP_TOP:
                pointer = -p - 1
            elif self.payload == OP_BOTTOM:
                pointer = p
                # TODO some more simplifications here

            if self.type_ == T_VAL:
                if self.payload == OP_POP:
                    return vm._reg_pop
                elif self.payload == OP_READ:
                    return vm._reg_read
                elif self.payload == OP_TEST:
                    return vm._reg_test
                elif self.payload.startswith('r'):
                    return getattr(vm, '_%s' % self.payload)
                else:
                    return vm._stk_data[pointer]
            elif self.type_ == T_REF:
                # return a position reference for caller to use
                self.sub_type = self.REF_REG
                if self.payload == OP_POP:
                    return self._reg_attr(OP_POP)
                elif self.payload == OP_READ:
                    return self._reg_attr(OP_READ)
                elif self.payload == OP_TEST:
                    return self._reg_attr(OP_TEST)
                elif self.payload.startswith('r'):
                    return '_%s' % self.payload
                else:
                    self.sub_type = self.REF_IDX
                    return pointer

    def _reg_attr(self, name):
        return '_'.join(['_reg', name])


    def __str__(self):
        return 'OP %s %s%s' % (self.type_,
                              self.payload,
                              ' (%s)' % self.param if self.param
                              else '')

    def __repr__(self):
        return str(self)
