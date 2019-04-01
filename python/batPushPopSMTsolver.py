from z3 import *


class Z3PushPopSubsetSolver:

    constraints = None
    soft_constraints = None
    s = None

    def __init__(self, constraints, hard_constraints, soft_constraints):
        self.constraints = constraints
        self.soft_constraints = soft_constraints
        self.s = Solver()
        self.s.push()
        for i in hard_constraints:
            if i < len(self.constraints):
                self.s.add(self.constraints[i])
            else:
                print("hard cons. with index " + str(i) + " is out of range for constraints array")
                exit(1)

    def check_subset(self, seed):
        self.s.push()
        self.add_soft_based_on_seed(seed)
        is_sat = (self.s.check() == sat)
        self.s.pop()
        return is_sat

    def get_soft_constraint_from_seed_index(self, index):
        group, cons_idx = self.soft_constraints[index]
        return self.constraints[cons_idx]

    def add_soft_based_on_seed(self, seed):
        for idx in seed:
            self.s.add(self.get_soft_constraint_from_seed_index(idx))