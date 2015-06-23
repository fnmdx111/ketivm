from .ast import make_ast_from
from spec.instructions import VIR_INST_LABEL
from vm.operand import Operand


def preprocess(fp):
    program_counter = 0
    labels = {}

    instructions = []

    for stmt in make_ast_from(fp):
        if stmt[0] == VIR_INST_LABEL:
            labels[stmt[1][0]] = program_counter
        else:
            instructions.append([stmt[0],
                                 list(map(Operand, stmt[1]))])
            program_counter += 1

    return instructions, labels
