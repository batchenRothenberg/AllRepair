from z3 import *
from z3printer import *
from batutils import find_regular_expression


def pretty_print_repair_expression(e):
    out = io.StringIO()
    # PP()(out, Formatter()(e)) # applying () to a class object calls the __call__ method of the class
    PP()(out, RepairFormatter()(e)) # applying () to a class object calls the __call__ method of the class
    return out.getvalue()


class RepairFormatter(object, Formatter):

    def __init__(self):
        Formatter.__init__(self)

    def pp_const(self, a):
        name = a.decl().name()
        res = find_regular_expression('::([^:]*)!',name)
        if res:
            pretty_name = res[0]
        else:
            new_res = find_regular_expression(':([^:]*)#', name)
            pretty_name = new_res[0]
        return to_format(pretty_name)

    def pp_bv(self, a):
        return to_format(a.as_signed_long())





