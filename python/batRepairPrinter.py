from z3 import *
from z3printer import *
from batutils import findall_regular_expression, match_regular_expression, search_regular_expression


def pretty_print_repair_expression(e):
    out = io.StringIO()
    # If e is a complex constraint due to loop unwinding, take the first conjunct
    if is_and(e):
        e = e.arg(0)
    # If e assigns to auxiliary guard - remove assignment
    assert is_eq(e)
    lhs = e.arg(0)
    rhs = e.arg(1)
    name = lhs.decl().name()
    is_name_a_guard = findall_regular_expression('goto_symex::.*guard', name)
    if is_name_a_guard:
        # PP()(out, Formatter()(rhs)) # Uncomment to disable pretty printing (e.g., for debugging)
        PP()(out, RepairFormatter()(rhs))  # applying () to a class object calls the __call__ method of the class
    else:
        # PP()(out, Formatter()(e)) # Uncomment to disable pretty printing (e.g., for debugging)
        PP()(out, RepairFormatter()(e)) # applying () to a class object calls the __call__ method of the class
    return out.getvalue()


class RepairFormatter(object, Formatter):

    def __init__(self):
        Formatter.__init__(self)

    def pp_const(self, a):
        name = a.decl().name()
        res = findall_regular_expression('^.*::(.*)$', name)  # remove scope prefix: 'g::f::x!3@4' to 'x!3@4'
        if res:
            name_without_scope = res[0]
        else:
            name_without_scope = name
        res = match_regular_expression('[^$?!@#]*', name_without_scope)  # remove SSA suffix: 'x!3@4' to 'x'
        if res:
            pretty_name = res.group()
        else:
            assert False  # should always match the empty string..
        return to_format(pretty_name)

    def pp_bv(self, a):
        return to_format(a.as_signed_long())





