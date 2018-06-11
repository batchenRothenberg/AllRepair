from z3 import *

def slice_program(sat_solution, smt_solution, assertion_constraints, constraints):
    assertions = [constraints[assertion_constraint] for assertion_constraint in assertion_constraints]
    # simplify assertion - get sub-expression which is already satisfied
    simpl_assertions = [find_satisfied_subexpression(assertion, smt_solution) for assertion in assertions]
    #print "simplified assert is " , simpl_assertion
    print "assertions are sat? " , [smt_solution.evaluate(simpl_assertion) for simpl_assertion in simpl_assertions]
    return [(-(x + 1)) for x in sat_solution]


def find_satisfied_subexpression(expr, smt_solution):
    ''' Given an expression expr which is satisfied by the smt_solution
    find a sub-expression of expr which is still satisfied by smt_solution,
    by breaking-down or sub-expressions .
    :param expr: original expression (z3 expression)
    :param smt_solution: an assignment to SMT variables (z3 model)
    :return: sub-expression of expr  satisfying smt_solution
    '''
    assert smt_solution.evaluate(expr)  # We assume the assertion is violated
    while is_or(expr):
        #print "expr is or"
        for conjunct in expr.children():
            print smt_solution.evaluate(conjunct)
            if is_true(smt_solution.evaluate(conjunct)):
                expr = conjunct
                print "breaking"
                break
    return expr