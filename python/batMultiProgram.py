from collections import Counter
from functools import reduce
from z3 import *
import re

from InGeneer import stmt
from batutils import Graph, get_vars_as_string, is_If


class batMultiProgram(Graph):

    constraints = []
    soft_constraints = []
    hard_constraints = []
    demand_constraints = []
    # var is mapped to the index of its assigning constraint, if exists
    assignment_map = {}
    sizes = []
    n = 0
    mutants = 0
    sat_seed = None     # Determines the chosen program
    smt_model = None    # Determines the chosen path within the program, leading to a bug.


    def __init__(self, filename, blocking_method):
        self.blocking_method = blocking_method
        self.read_constraints(filename)
        print("total cons:", len(self.constraints), "total hard+soft:", len(self.soft_constraints) + len(
            self.hard_constraints))
        self.mutants = reduce(lambda x, y: x * y, self.sizes)
        print("Total number of mutated programs:", self.mutants)

    def read_constraints(self, filename):
        self.constraints = self.read_smt2(filename)
        self.read_group_smt2(filename)
        if (len(self.soft_constraints) == 0):
            print(
                "All constraints belong to group number {0}. For repair, add alternatives under a positive group number.")
            exit(0)
        self.soft_constraints = sorted(self.soft_constraints)
        self.sizes = [y for (x, y) in sorted(Counter(x for (x, y) in self.soft_constraints).items())]
        self.n = len(self.soft_constraints)

    def read_smt2(self, filename):
        formula = parse_smt2_file(filename)
        if is_and(formula):
            return formula.children()
        else:
            return [formula]

    def read_group_smt2(self, filename):
        f = open(filename)  # already checked before that file exists
        cons_i = 0
        soft_i = 0
        for line in f.readlines():
            p = re.compile(';AllRepair *\{([0-9,a-z]*)\}')
            res = p.findall(line)
            if res != []:
                # add constraint to hard/soft constraints
                if res[0] == '0' or res[0] == 'demand':
                    self.hard_constraints.append(cons_i)
                else:
                    self.soft_constraints.append((int(res[0]), cons_i))
                    soft_i = soft_i + 1
                # if assert or assume - add to assert_and_assume list. Otherwise - it's an assignment, add to map.
                if self.blocking_method != "basic":
                    if res[0] == 'demand':
                        self.demand_constraints.append(cons_i)
                    else:
                        cons = self.constraints[cons_i]
                        if is_and(cons): # compound constraint due to loop unwinding
                            assigns = cons.children()
                        else:
                            assigns = [cons]
                        for ass in assigns:
                            assert is_eq(ass)
                            assert ass.num_args() > 1
                            assert is_const(ass.arg(0))
                            if str(ass.arg(0)) not in self.assignment_map:
                                if res[0] == '0': # phi-function or hard constraint that is not an assert or assume (e.g., cbmc init)
                                    self.assignment_map[str(ass.arg(0))] = DependencyTransition(None, ass)
                                else: # soft constraint
                                    self.assignment_map[str(ass.arg(0))] = DependencyTransition(soft_i-1, ass) # soft_i was already increased
                cons_i = cons_i + 1
        print(self.demand_constraints)
        print(self.assignment_map)
        f.close()

    def get_original_index(self, group):
        return next((idx, cons_i) for idx, (g, cons_i) in enumerate(self.soft_constraints) if g == group)

    def get_children(self, variable_str):
        cons = None
        if variable_str in self.assignment_map.keys():
            cons = self.assignment_map[variable_str].expr
        if cons is None:
            return []
        else:
            assert is_eq(cons)
            rhs = cons.arg(1)
            if is_If(rhs):  # phi-function assignment
                guard = rhs.arg(0)
                if is_true(self.smt_model.evaluate(guard)):
                    return [str(guard),str(rhs.arg(1))]
                else:
                    return [str(guard),str(rhs.arg(2))]
            else: # standard assignment
                return get_vars_as_string(rhs)

    @staticmethod
    def unwind_cons(cons, v):
        if is_and(cons):  # cons is the result of loop/function unwinding. Find the assignment to v in it.
            for child in cons.children():
                assert is_eq(child)
                if str(child.arg(0).decl()) == v:
                    return child
        else:  # cons is an assignment (phi-function, condition or standard assignment)
            assert is_eq(cons)
            return cons

    def get_dependency_transitions_from_var(self, v):
        res = None, None
        if v in self.assignment_map.keys():
            sort, index = self.assignment_map[v]
            if sort == 'H':
                cons = self.constraints[index]
                l_1, l_2 = self.get_dependency_transitions_for_hard(cons,v)
                res = l_1, l_2
            else:
                assert (sort == 'S')
                group_num, cons_index_of_original = self.soft_constraints[index]
                original_cons = self.constraints[cons_index_of_original]
                t = DependencyTransition(index, batMultiProgram.unwind_cons(original_cons, v))
                l_1 = [t]
                while index + 1 < len(self.soft_constraints):
                    index = index + 1
                    next_group_num, next_cons_index = self.soft_constraints[index]
                    if next_group_num == group_num:
                        cons = self.constraints[next_cons_index]
                        t = DependencyTransition(index, batMultiProgram.unwind_cons(cons, v))
                        l_1.append(t)
                    else:
                        break
                res = l_1, None
        return res

    def get_dependency_transitions_for_hard(self, cons, v):
        unwound_cons = batMultiProgram.unwind_cons(cons, v)
        assert is_eq(unwound_cons)
        lhs = unwound_cons.arg(0)
        rhs = unwound_cons.arg(1)
        if is_If(rhs):
            guard = rhs.arg(0)
            true_var = rhs.arg(1)
            false_var = rhs.arg(2)
            model_result = self.smt_model.evaluate(guard)
            if is_true(model_result):
                return [DependencyTransition(None, guard)], [DependencyTransition(None, lhs == true_var)]
            else:
                return [DependencyTransition(None, Not(guard))], [DependencyTransition(None, lhs==false_var)]
        return [DependencyTransition(None, unwound_cons)], None

    def get_multitrace_from_var_list(self, var_list):
        res = []
        for l_1,l_2 in [self.get_dependency_transitions_from_var(v) for v in var_list]:
            if l_1:
                res.append(l_1)
            if l_2:
                res.append(l_2)
        return res

    def get_root_variables(self):
        return get_vars_as_string(And([self.constraints[i] for i in self.demand_constraints]))

    def get_initial_formula_from_demands(self):
        return And([self.constraints[i] for i in self.demand_constraints])


class DependencyTransition(stmt.Stmt):

    def __init__(self, literal, expr):
        self.literal = literal
        super(DependencyTransition, self).__init__(expr)
        if self.is_assignment():
            self.lhs = self.expr.arg(0)
            self.rhs = self.expr.arg(1)
        else:
            self.lhs = None
            self.rhs = None

    def __str__(self):
        if self.is_assignment():
            assign_stmt = stmt.AssignmentStmt(self.expr)
            return "(" + str(self.literal) + ": " + str(assign_stmt) + ") "
        else:
            return "(" + str(self.literal) + ": " + str(self.expr) + ") "

    def __repr__(self):
        return str(self)

    def is_assignment(self):
        return is_eq(self.expr)

    def is_condition(self):
        return not self.is_assignment()
