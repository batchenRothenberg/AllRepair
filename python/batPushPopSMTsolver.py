from z3 import *


class Z3PushPopSubsetSolver:

    constraints = None
    s = None

    def __init__(self, constraints, hard_constraints):
        self.constraints = constraints
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
        # TODO: add soft constraints based on seed
        print("seed is "+str(seed))
        is_sat = (self.s.check() == sat)
        self.s.pop()
        return is_sat