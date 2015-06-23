Keti VM
====

It's a simple toy. An assembly-like language is created for this VM. See
`sample.ket` and `sample-reg.ket` for details.

`sample.ket` is a code sample which, using only stack, calculates the square
 root of user's input, while `sample-reg.ket` uses only registers as memory.

Keti VL (virtual language) specification
----

### Instructions

It's an assembly-like language. Basic instructions are listed in
`spec/instructions.py`.

Almost all binary instructions can have up to three parameters:

    inst op1, op2, op3 (1)
    inst op1, op2      (2)
    inst op1           (3)
    inst               (4)

1. this means that the result of `op1` and `op2` is put into `op3`;

2. this means that the result of `op1` and `op2` is pushed into stack;

3. this means that the result of `op1` and the top of stack (popped) is pushed
back to stack, i.e. `push op1 \n inst` or `pop \n inst @pop, op1`;

4. this means that the result of the two elements at the top of stack (both
popped) is pushed back into stack.

Almost all unary instructions can have up to two parameters:

    inst op1, op2 (1)
    inst op1      (2)
    inst          (3)

1. this means that the result of `op1` is put into `op2`;

2. this means that the result of `op1` is put back into `op1` (it's slightly
different than the syntax of binary instructions, but it's still not final);

3. this means that the result of top of stack is put back into the top of stack.


### Operands

Operands are parameters to instructions. Available reserved operands can be
found at `spec/identifiers.py`.

Operands are typically formed as

    [INDICATOR]IDENTIFIER[(PARAMETER)]

Parts in brackets are omittable. Indicators indicate the type of operands. Keti
VL currently supports four: macro (`#`), val (`@`), label (`:`) and blank.
Identifier is the ID for the operand. And parameter is used to make things more
flexible.

A macro operand means that you can perform extra actions when referencing them.
And val operand enables you referencing the value within the identifier.
For example, by executing `push #read`, you can read from standard input, save
the input in register `read` and push the content in register `read` into the
stack, while `push @read` only does the push. Quick tip: macro operands without
the macro indicators are valid instructions, e.g. `pop` pops the stack and save
the popped element into register `pop`.

Using terms like `@top` and `@bottom(1)`, you can access the top element of the
stack and the element next to the bottom of the stack. The language can be very
flexible if you put val operands and parameters into use. Parameters are simply
operands. This suggests terms such as `@top(@top)` and `@top(@r1)` are valid
operands.

### Special instructions

There presents virtual instruction in Keti VL, i.e. the label instruction, which
labels segments of codes and is not present in parsed code.

For debugging programs in Keti VL, instruction `int` comes in handy. When
executing this instruction, the Keti VM loads a debugging console into the
frontend, enabling viewing of the state of VM. For available commands, see
`vm/keti.py:int`.

### Implementation details

Please refer to the codes.

License
----

This project and its all related projects are licensed under GPLv3. Search and
obtain a copy of it if you want.
