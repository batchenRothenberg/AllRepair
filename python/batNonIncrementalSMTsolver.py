from z3 import *


class Z3NonIncrementalSubsetSolver:

    constraints = None
    hard_constraints = None
    s = None

    def __init__(self, constraints, hard_constraints):
        self.constraints = constraints
        self.hard_constraints = hard_constraints

    def check_subset(self, seed):
        self.s = Solver()
        for i in self.hard_constraints:
            if i < len(self.constraints):
                self.s.add(self.constraints[i])
            else:
                print("hard cons. with index " + str(i) + " is out of range for constraints array")
                exit(1)
        #Todo: add soft constraints based on seed
        print("seed is "+str(seed))
        is_sat = (self.s.check() == sat)
        return is_sat
