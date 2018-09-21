from collections import Counter
from functools import reduce
from z3 import *
import re


class batMultiProgram:

    constraints = []
    soft_constraints = []
    hard_constraints = []
    demand_constraints = []
    # var is mapped to the index of its assigning constraint, if exists
    assignment_map = {}
    sizes = []
    n = 0
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
        for line in f.readlines():
            p = re.compile(';AllRepair *\{([0-9,a-z]*)\}')
            res = p.findall(line)
            if res != []:
                # add constraint to hard/soft constraints
                if res[0] == '0' or res[0] == 'demand':
                    self.hard_constraints.append(cons_i)
                else:
                    self.soft_constraints.append((int(res[0]), cons_i))
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
                                self.assignment_map[ass.arg(0).__str__()] = cons_i
                cons_i = cons_i + 1
        print(self.demand_constraints)
        print(self.assignment_map)
        f.close()

    def get_original_index(self, group):
        return next((idx, cons_i) for idx, (g, cons_i) in enumerate(self.soft_constraints) if g == group)



