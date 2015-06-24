
from spec.instructions import VIR_INST_LABEL
from .op_parser import parse


def preprocess(fp):
    program_counter = 0
    labels = {}

    instructions = []

    for stmt in parse(fp):
        if stmt[0] == VIR_INST_LABEL:
            labels[stmt[1][0](None)] = program_counter
        else:
            instructions.append(stmt)
            program_counter += 1

    return instructions, labels
