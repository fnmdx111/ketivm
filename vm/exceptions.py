
class InvalidMacro(Exception):
    def __init__(self, macro_name, vm):
        super(InvalidMacro, self).__init__('invalid macro "%s"'
                                           ' at IP=%s.'
                                           % (macro_name, vm._inst_ptr))

class AccessViolation(Exception):
    def __init__(self, vm):
        super(AccessViolation, self).__init__('instruction pointer'
                                              ' pointed to invalid address'
                                              ' %s' % vm._inst_ptr)
