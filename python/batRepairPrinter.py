from z3 import *
from z3printer import *


def pretty_print_repair_expression(e):
    out = io.StringIO()
    PP()(out, Formatter()(e))
    return out.getvalue()
    #return "pretty repair: " + obj_to_string(e)
    #oldFormater = _Formatter
    #_Formatter = RepairFormatter()
    #print e
    #_Formatter = oldFormater


class RepairFormatter(Formatter):
    def __init__(self, e):
        super.__init__(e)
