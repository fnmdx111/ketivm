from functools import wraps
import sys
from .operand import Operand, IND_MACRO_CALL, OP_POP
from spec.instructions import *

def inst_to_attr(inst):
    return inst.replace('-', '_').lower()

def regular_inst(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        f(self, *args, **kwargs)
        self._inst_ptr += 1

    return wrapper


class KetiVM:
    def init_state(self):
        self._stk_data = []
        self._stk_inst_ptr = []

        self._inst = []
        self._inst_ptr = 0
        self._abs_label_dict = {}

        self._reg_read = ''

        self._r0 = None

        self._r1 = None
        self._r2 = None
        self._r3 = None
        self._r4 = None
        self._r5 = None
        self._r6 = None
        self._r7 = None
        self._r8 = None

        self._reg_test = None

    def __init__(self):
        self.init_state()

        self.O = lambda ref: Operand(ref, vm=self)

    def _gen_op_mpop(self):
        return self.O(''.join([IND_MACRO_CALL,
                               OP_POP]))

    def mul0(self):
        o2 = self._gen_op_mpop()
        o1 = self._gen_op_mpop()
        self.mul2(o1, o2)

    @regular_inst
    def mul2(self, op1, op2):
        o1 = op1(self)
        o2 = op2(self)
        # clarifying the sequence of argument evaluating,
        # i.e. it's from left to right
        self._stk_data.append(o1 * o2)

    def mul(self, *args):
        if len(args) == 2:
            self.mul2(*args)
        else:
            self.mul0()

    @regular_inst
    def sub2(self, op1, op2):
        o1 = op1(self)
        o2 = op2(self)
        self._stk_data.append(o1 - o2)

    def sub0(self):
        o2 = self._gen_op_mpop()(self)
        o1 = self._gen_op_mpop()(self)
        self.sub2(self.O(o1), self.O(o2))

    def sub(self, *args):
        if len(args) == 2:
            self.sub2(*args)
        else:
            self.sub0()

    def add0(self):
        o2 = self._gen_op_mpop()
        o1 = self._gen_op_mpop()
        self.add2(o1, o2)

    @regular_inst
    def add2(self, op1, op2):
        o1 = op1(self)
        o2 = op2(self)
        self._stk_data.append(o1 + o2)

    def add(self, *args):
        if len(args) == 2:
            self.add2(*args)
        else:
            self.add0()

    @regular_inst
    def div2(self, op1, op2):
        o1 = op1(self)
        o2 = op2(self)
        self._stk_data.append(o1 / o2)

    def div0(self):
        o1 = self._gen_op_mpop()(self)
        o2 = self._gen_op_mpop()(self)
        self.div2(self.O(o2), self.O(o1))

    def div(self, *args):
        if len(args) == 2:
            self.div2(*args)
        else:
            self.div0()

    @regular_inst
    def push(self, op):
        self._stk_data.append(op(self))

    def push_int(self, op):
        self.push(lambda vm: int(op(self)))

    @regular_inst
    def inc_top(self):
        self._stk_data[-1] += 1

    @regular_inst
    def dec_top(self):
        self._stk_data[-1] -= 1

    @regular_inst
    def print(self, op):
        print(op(self), end='')

    def print_top(self):
        self.print(self.O('@top'))

    @regular_inst
    def println(self, op):
        print(op(self))

    def println_top(self):
        self.println(self.O('@top'))

    def label(self, name, ptr=0):
        self._abs_label_dict[name] = ptr or self._inst_ptr

    @regular_inst
    def test(self, op1, op2):
        self._reg_test = op1(self) - op2(self)

    @regular_inst
    def test_top(self):
        self._reg_test = self._stk_data[-1]

    @regular_inst
    def pop(self):
        self._stk_data.pop()

    def _inc_ip(self):
        self._inst_ptr += 1

    def jplt(self, op):
        if self._reg_test < 0:
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()

    def jple(self, op):
        if self._reg_test <= 0:
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()

    def jpgt(self, op):
        if self._reg_test > 0:
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()

    def jpge(self, op):
        if self._reg_test >= 0:
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()

    def jpeq(self, op):
        if self._reg_test == 0:
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()

    def jpne(self, op):
        if self._reg_test != 0:
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()

    def jump(self, op):
        self._inst_ptr = self._abs_label_dict[op(self)]

    def call(self, op):
        self._stk_inst_ptr.append(self._inst_ptr + 1)
        self._inst_ptr = self._abs_label_dict[op(self)]

    def ret(self):
        self._inst_ptr = self._stk_inst_ptr.pop()

    def error(self, op):
        raise op(self)

    def exit(self):
        sys.exit()

    def install_instructions(self, inst):
        self._inst.extend(inst)
        self._inst.append(INST_HALT)

    def install_labels(self, labels):
        self._abs_label_dict.update(labels)

    def inst_streaming(self):
        while True:
            inst_name, args = self._inst[self._inst_ptr]
            attr_name = inst_to_attr(inst_name)

            if inst_name == INST_HALT:
                break

            getattr(self, attr_name, lambda _: _)(*args)
            # FIXME potential bug here: empty `args' may lead id_func erring
