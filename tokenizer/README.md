Parsers
====

Keti VL parser
----

Grammar is

    stmt -> line_number INST operand NEW_LINE
          | line_number INST NEW_LINE
    INST = idtf
    NEW_LINE = \n

    line_number -> LINE_NUMBER?
    LINE_NUMBER = \d+

    operand -> OP SC OP SC OP
             | OP SC OP
             | OP
    OP = idtf
    SC = [,\s]

Instead of using libraries such as Ply, I wrote a FSM from scratch. The graph is
as belows:

![parser_graph](_img/fsm_parser.png)

Operand parser
----

Operands are a bit complicated: it has indicators, identifiers and parameters,
i.e.:

    operand -> INDICATOR? IDENTIFIER parameter
    INDICATOR = #|@
    IDENTIFIER = idtf

    ;; strings don't agree with this grammar although they are handled by the
    ;; same FSM

    parameter -> LPAREN operand RPAREN
    LPAREN = (
    RPAREN = )
    

What's worse, parameters are defined to be valid operand **objects**. I don't
think this is what can be handled by pure FSM. However, the majority of the
operand parser is implemented utilizing FSM.

The graph is as belows:

![op_graph](_img/fsm_op.png)
