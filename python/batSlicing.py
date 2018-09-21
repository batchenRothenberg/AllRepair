from z3 import *
#from z3util import get_vars
from batutils import *

_debug_slicing = False
_simplification_flag = True

def slice_program(sat_solution, smt_solution, assert_and_assume_constraints, constraints, assigning_constraint_map, soft_constraints):
    demands = [constraints[cons_i] for cons_i in assert_and_assume_constraints]
    # simplify assertion or assumption - get sub-expression which is already satisfied
    simpl_demands = [find_satisfied_subexpression(demand, smt_solution) for demand in demands]
    if _debug_slicing:
        print("simpl_demands ", simpl_demands)
        print ([smt_solution.evaluate(simpl_demand) for simpl_demand in simpl_demands])
    # START SLICING
    relevant_constraints = set(assert_and_assume_constraints)
    if _simplification_flag:
        relevant_vars = [var.__str__() for var in get_impacting_vars(And(demands),smt_solution)]
    else:
        relevant_vars = [var.__str__() for var in get_vars(Or(simpl_demands))]
    # TODO: optimization: move calculation up to here to be done once in init, without simplification
    unproccesed_vars_stack = list(relevant_vars)
    while unproccesed_vars_stack:
        var = unproccesed_vars_stack.pop()
        if var.__str__() in assigning_constraint_map:
            assigning_constraint_index = assigning_constraint_map[var.__str__()]
            assigning_constraint = constraints[assigning_constraint_index]
            relevant_constraints.add(assigning_constraint_index)
            # split conjoined loop constraint
            if is_and(assigning_constraint):
                for child in assigning_constraint.children():
                    assert is_eq(child)
                    if child.arg(0).decl().__str__() == var.__str__():
                        assigning_constraint = child
            # get right-hand-side of assignment
            assert is_eq(assigning_constraint)
            rhs = assigning_constraint.arg(1)
            if rhs.decl().__str__()=="If": # phi function assignment
                # Add guard variables anyway
                guard = rhs.arg(0)
                if _simplification_flag:
                    new_vars = get_impacting_vars(guard,smt_solution)
                else:
                    new_vars = get_vars(find_satisfied_subexpression(guard, smt_solution))
                # Add variables of relevant branch only
                if is_true(smt_solution.evaluate(guard)):
                    if _debug_slicing:
                        print(guard, " is true")
                    if _simplification_flag:
                        new_vars.extend(get_impacting_vars(rhs.arg(1),smt_solution))
                    else:
                        new_vars.extend(get_vars(rhs.arg(1),smt_solution))
                else:
                    if _debug_slicing:
                        print(guard, " is false")
                    if _simplification_flag:
                        new_vars.extend(get_impacting_vars(rhs.arg(2),smt_solution))
                    else:
                        new_vars.extend(get_vars(rhs.arg(2),smt_solution))
            else: # standard assignment
                if _simplification_flag:
                    new_vars = get_impacting_vars(rhs,smt_solution)
                else:
                    new_vars = get_vars(find_satisfied_subexpression(rhs, smt_solution))
            # Add new_vars to stuck, only if never added before
            for new_var in new_vars:
                if not new_var.__str__() in relevant_vars:
                    relevant_vars.append(new_var.__str__())
                    unproccesed_vars_stack.append(new_var.__str__())
    if _debug_slicing:
        print("relevant_cons: ", relevant_constraints)
        print("relevant variables: ", relevant_vars)
    return get_blocking_clause_from_constraints(soft_constraints,relevant_constraints,sat_solution)


def get_blocking_clause_from_constraints(soft_constraints, relevant_constraints, sat_solution):
    relevant_indices = [i for i in range(0, len(soft_constraints) - 1) if
                        soft_constraints[i][1] in relevant_constraints]
    # relevant_indices always contain only original (unmutated) constraints.
    # Now we replace them with the actual constraints chosen by the SAT solver.
    # We assume mutations did not change the variables used.
    actual_indices = []
    for index in relevant_indices:
        while index not in sat_solution:
            index = index + 1
        actual_indices.append(index)
    if _debug_slicing:
        print("sat solution: ", sat_solution)
        print("actual indices: ", actual_indices)
    assert set(actual_indices) <= set(sat_solution)
    return [(-(x + 1)) for x in actual_indices]

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
            print(smt_solution.evaluate(conjunct))
            if is_true(smt_solution.evaluate(conjunct)):
                expr = conjunct
                print("breaking")
                break
    return expr


def get_impacting_vars(f, smt_solution, rs=[]):
    if __debug__:
        assert is_expr(f)
    # base cases
    if is_const(f):
        if is_expr_val(f):
            return rs
        else:  #variable
            return vset(rs + [f],str)
    # recursive calls
    else:
        #print "else"
        if is_and(f) and is_false(smt_solution.evaluate(f)):
            for arg in f.children():
                if is_false(smt_solution.evaluate(arg)):
                    rs = get_impacting_vars(arg,smt_solution,rs)
                    break
        elif is_or(f) and is_true(smt_solution.evaluate(f)):
            for arg in f.children():
                if is_true(smt_solution.evaluate(arg)):
                    rs = get_impacting_vars(arg,smt_solution,rs)
                    break
        else:
            for arg in f.children():
                rs = get_impacting_vars(arg, smt_solution, rs)
        return vset(rs, str)
