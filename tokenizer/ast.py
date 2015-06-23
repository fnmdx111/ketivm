from .tknz import MyFSM
from itertools import chain


def make_ast_from(fp):
    my_fsm = MyFSM(MyFSM.NEW_LINE)

    ast = []
    tokens = my_fsm.tokens_of(chain.from_iterable(fp))

    for type_, token in tokens:
        if type_ == MyFSM.INSTRUCTION:
            ast.append([token, []])
        elif type_ == MyFSM.IDENTIFIER:
            ast[-1][-1].append(token)

    return ast


if __name__ == '__main__':
    with open('../sample.ket', 'r') as f:
        make_ast_from(f)
