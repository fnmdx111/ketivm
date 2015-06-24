from functools import wraps
import operator as oprt
import sys
from .operand import OP_POP, Operand
from spec.identifiers import IND_MACRO, T_REF
from spec.instructions import *
from tokenizer.op_parser import make_operand
from vm.exceptions import AccessViolation


def inst_to_attr(inst):
    return inst.replace('-', '_').lower()

def regular_inst(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        f(self, *args, **kwargs)
        self._inst_ptr += 1

    return wrapper

def _sv(x):
    # generate a single-valued function
    # I really have no idea how to build this vm with C, despite the fact
    # that C can perform FP to some extent
    def wrapper(_):
        return x
    return wrapper


class KetiVM:
    def init_state(self):
        self._stk_data = []
        self._stk_inst_ptr = []

        self._inst = []
        self._inst_ptr = 0
        self._abs_label_dict = {}

        self._reg_read = ''
        self._reg_pop = None
        self._reg_test = None

        self._int = False

        for i in range(9):
            setattr(self, '_r%d' % i, None)

    def __init__(self):
        self.init_state()

    def _gen_op_mpop(self):
        return make_operand(''.join([IND_MACRO, OP_POP]))

    def _internal_pop(self):
        self._reg_pop = self._stk_data.pop()
        return self._reg_pop

    @regular_inst
    def push(self, op):
        self._stk_data.append(op(self))

    def push_int(self, op):
        self.push(lambda vm: int(op(self)))

    @regular_inst
    def read(self):
        self._reg_read = input()

    @regular_inst
    def read_int(self):
        self._reg_read = int(input())

    @regular_inst
    def read_float(self):
        self._reg_read = float(input())

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
        self.print(make_operand('@top'))

    @regular_inst
    def println(self, op):
        print(op(self))

    def println_top(self):
        self.println(make_operand('@top'))

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
        self._internal_pop()

    def _inc_ip(self):
        self._inst_ptr += 1

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

    def exec_next_inst(self):
        inst_name, args = self._inst[self._inst_ptr]
        attr_name = inst_to_attr(inst_name)

        if inst_name == INST_HALT:
            return False
        if self._int:
            if attr_name == 'int':
                self._inst_ptr += 1
                return True

        getattr(self, attr_name, lambda _: _)(*args)
        # FIXME potential bug here: empty `args' may lead id_func erring

        return True

    def inst_streaming(self):
        try:
            while self.exec_next_inst():
                pass
        except IndexError:
            raise AccessViolation(self)

    def int(self):
        self._inst_ptr += 1
        names = []
        mon_stk = False
        mon_ip = True

        self._int = True

        while True:
            cmd = input('int cmd? ')
            if cmd == 'ret':
                break

            elif cmd == 'regs':
                print(' '.join(['r%s: %s' % (i, getattr(self, '_r%s' % i))
                                for i in range(9)]))

            elif cmd.startswith('mon'):
                if cmd == 'mon clr':
                    names.clear()
                else:
                    for name in cmd.split()[1:]:
                        if name == 'stk':
                            mon_stk = not mon_stk
                        elif name == 'ip':
                            mon_ip = not mon_ip
                        else:
                            if name not in names:
                                names.append(name)
                            else:
                                names.remove(name)

            elif cmd == 'stk':
                print(self._stk_data)

            elif cmd == 'rstk':
                print(self._stk_inst_ptr)

            elif cmd == 'ip':
                print('ip: %s' % self._inst_ptr)
                print('inst: %s' % self._inst[self._inst_ptr])

            elif cmd == 'inst':
                print(self._inst)

            elif cmd == 'cont' or cmd == '':
                self.exec_next_inst()
                if names:
                    print(', '.join(['%s: %s' % (n, getattr(self, n))
                                    for n in names]))
                if mon_stk:
                    print(self._stk_data)
                if mon_ip:
                    print('ip: %s' % self._inst_ptr)
                    print('next inst: %s' % self._inst[self._inst_ptr])

            elif cmd == 'skip':
                self._inst_ptr += 1
                print('ip: %s' % self._inst_ptr)
                print('next inst: %s' % self._inst[self._inst_ptr])

        self._int = False

    def move2(self, op1, op2):
        o1 = op1(self)

        o2 = op2(self)
        assert op2.type_ == T_REF

        if op2.sub_type == Operand.REF_IDX:
            self._stk_data[o2] = o1
        elif op2.sub_type == Operand.REF_REG:
            setattr(self, o2, o1)

    def move1(self, op):
        o = op(self)
        self._stk_data[-1] = o

    def move0(self):
        self._stk_data[-1] = self._r1

    @regular_inst
    def move(self, *args):
        argc = len(args)
        if argc == 0:
            self.move0()
        elif argc == 1:
            self.move1(*args)
        elif argc == 2:
            self.move2(*args)



def install_binary_family(name, f):
    def fn(argc):
        return '%s%s' % (name, argc)

    def _0(self):
        o2 = self._internal_pop()
        o1 = self._internal_pop()
        self._stk_data.append(f(o1, o2))
    setattr(KetiVM, fn(0), _0)

    def _1(self, op):
        o = op(self)
        self._stk_data[-1] = f(self._stk_data[-1], o)
    setattr(KetiVM, fn(1), _1)

    def _2(self, op1, op2):
        o1 = op1(self)
        o2 = op2(self)
        self._stk_data.append(f(o1, o2))
    setattr(KetiVM, fn(2), _2)

    def _3(self, op1, op2, op3):
        o1 = op1(self)
        o2 = op2(self)

        o3 = op3(self)
        assert op3.type_ == T_REF

        result = f(o1, o2)
        if op3.sub_type == Operand.REF_IDX:
            self._stk_data[o3] = result
        elif op3.sub_type == Operand.REF_REG:
            setattr(self, o3, result)
    setattr(KetiVM, fn(3), _3)

    @regular_inst
    def _(self, *args):
        argc = len(args)
        getattr(self, fn(argc))(*args)
    setattr(KetiVM, name, _)

for name, f in zip((INST_MUL, INST_ADD, INST_SUB, INST_DIV, INST_IDIV,
                    INST_LSH, INST_RSH,
                    INST_AND, INST_OR, INST_XOR, INST_MOD, INST_POW),
                   (oprt.mul, oprt.add, oprt.sub, oprt.truediv, oprt.floordiv,
                    oprt.lshift, oprt.rshift,
                    oprt.and_, oprt.or_, oprt.xor, oprt.mod, oprt.pow)):
    install_binary_family(name, f)


def install_unary_family(name, f):
    def fn(argc):
        return '%s%s' % (name, argc)

    def _0(self):
        o = self._internal_pop()
        self._stk_data.append(f(o))
    setattr(KetiVM, fn(0), _0)

    def _1(self, op):
        o = op(self)

        if op.type_ == T_REF:
            if op.sub_type == Operand.REF_IDX:
                self._stk_data[o] = f(self._stk_data[o])
            elif op.sub_type == Operand.REF_REG:
                o_val = getattr(self, o)
                setattr(self, o, f(o_val))
        else:
            self._stk_data[o] = f(self._stk_data[o])
    setattr(KetiVM, fn(1), _1)

    def _2(self, op1, op2):
        o1 = op1(self)

        o2 = op2(self)
        assert op2.type_ == T_REF

        result = f(o1)
        if op2.sub_type == Operand.REF_IDX:
            self._stk_data[o2] = result
        elif op2.sub_type == Operand.REF_REG:
            setattr(self, o2, result)
    setattr(KetiVM, fn(2), _2)

    @regular_inst
    def _(self, *args):
        argc = len(args)
        getattr(self, fn(argc))(*args)
    setattr(KetiVM, name, _)

for name, func in zip((INST_INC, INST_DEC, INST_NEG, INST_NOT, INST_ABS),
                      (lambda x: x + 1, lambda x: x - 1, oprt.neg, oprt.inv,
                       oprt.abs)):
    install_unary_family(name, func)


def install_jump_family(name, f):
    def _(self, op):
        if f(self._reg_test, 0):
            self._inst_ptr = self._abs_label_dict[op(self)]
        else:
            self._inc_ip()
    setattr(KetiVM, name, _)

for name, func in zip((INST_JPLT, INST_JPLE, INST_JPGT, INST_JPGE,
                       INST_JPEQ, INST_JPNE),
                      (oprt.lt, oprt.le, oprt.gt, oprt.ge,
                       oprt.eq, oprt.ne)):
    install_jump_family(name, func)
