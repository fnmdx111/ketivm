from tokenizer.preprocessor import preprocess
from vm.keti import KetiVM

def execute(path):
    with open(path, 'r') as f:
        instructions, labels = preprocess(f)

        keti = KetiVM()
        keti.install_instructions(instructions)
        keti.install_labels(labels)

        keti.inst_streaming()

if __name__ == '__main__':
    execute('sample-reg.ket')
