from collections import Counter
from functools import reduce
from z3 import *
import re

from InGeneer import stmt
from batutils import Graph, get_vars_as_string

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
                            if ass.arg(0).__str__() not in self.assignment_map:
                                if res[0] == '0': # phi-function
                                    self.assignment_map[ass.arg(0).__str__()] = ('H', cons_i)
                                else: # soft constraint
                                    self.assignment_map[ass.arg(0).__str__()] = ('S', soft_i-1) # soft_i was already increased
                cons_i = cons_i + 1
        print(self.demand_constraints)
        print(self.assignment_map)
        f.close()

    def get_original_index(self, group):
        return next((idx, cons_i) for idx, (g, cons_i) in enumerate(self.soft_constraints) if g == group)

    def get_children(self, variable_str):
        cons = self.get_unwound_assigning_cons_from_var(variable_str)
        if cons is None:
            return []
        else:
            assert is_eq(cons)
            rhs = cons.arg(1)
            if rhs.decl().__str__() == "If":  # phi-function assignment
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

    def get_unwound_assigning_cons_from_var(self, v):
        if v in self.assignment_map.keys():
            type, index = self.assignment_map[v]
            if type == 'H':
                cons = self.constraints[index]
            else:
                assert (type == 'S')
                group_num, cons_index = self.soft_constraints[index]
                cons = self.constraints[cons_index]
            return batMultiProgram.unwind_cons(cons, v)
        else: # variable is an input variable.
            return None

    def get_dependency_transitions_from_var(self, v):
        res = None
        if v in self.assignment_map.keys():
            sort, index = self.assignment_map[v]
            if sort == 'H':
                cons = self.constraints[index]
                t = DependencyTransition(None, batMultiProgram.unwind_cons(cons, v))
                res = [t]
            else:
                assert (sort == 'S')
                group_num, cons_index_of_original = self.soft_constraints[index]
                original_cons = self.constraints[cons_index_of_original]
                t = DependencyTransition(index, batMultiProgram.unwind_cons(original_cons, v))
                res = [t]
                while index + 1 < len(self.soft_constraints):
                    index = index + 1
                    next_group_num, next_cons_index = self.soft_constraints[index]
                    if next_group_num == group_num:
                        cons = self.constraints[next_cons_index]
                        t = DependencyTransition(index, batMultiProgram.unwind_cons(cons, v))
                        res.append(t)
                    else:
                        break
        return res

    def get_multitrace_from_var_list(self, var_list):
        return [y for y in (self.get_dependency_transitions_from_var(v) for v in var_list) if y]

    def get_root_variables(self):
        return get_vars_as_string(And([self.constraints[i] for i in self.demand_constraints]))

    def get_initial_formula_from_demands(self):
        return And([self.constraints[i] for i in self.demand_constraints])


class DependencyTransition(stmt.AssignmentStmt):

    def __init__(self, literal, expr):
        self.literal = literal
        super(DependencyTransition, self).__init__(expr)

    def __str__(self):
        return "(" + str(self.literal) + ": " + super(DependencyTransition, self).__str__() + ") "
