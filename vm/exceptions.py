
class InvalidMacro(Exception):
    def __init__(self, macro_name, vm):
        super(InvalidMacro, self).__init__('invalid macro "%s"'
                                           ' at IP=%s.'
                                           % (macro_name, vm._inst_ptr))
