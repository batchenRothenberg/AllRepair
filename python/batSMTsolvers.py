from collections import deque
from z3 import *


def dimacs_var(i):
    if i not in dimacs_var.cache:
        if i > 0:
            dimacs_var.cache[i] = Bool(str(i))
        else:
            dimacs_var.cache[i] = Not(Bool(str(-i)))
    return dimacs_var.cache[i]


dimacs_var.cache = {}


def read_dimacs(filename):
    formula = []
    with open(filename) as f:
        for line in f:
            if line.startswith('c') or line.startswith('p'):
                continue
            clause = [int(x) for x in line.split()[:-1]]
            formula.append(Or(dimacs_var(i) for i in clause))
    return formula


class Z3SubsetSolver:
    c_prefix = "!marco"  # to differentiate our vars from instance vars

    assigned_to = []  # bat
    n = 0
    s = None
    varcache = {}
    idcache = {}

    def __init__(self, constraints, hard_constraints, soft_constraints):
        self.make_solver(constraints, hard_constraints, soft_constraints)

    def make_solver(self, constraints, hard_constraints, soft_constraints):
        self.s = Solver()
        for i in hard_constraints:
            if i < len(constraints):
                self.s.add(constraints[i])
            else:
                print("hard cons. with index " + str(i) + " is out of range for constraints array")
        for idx, (group, cons_i) in enumerate(soft_constraints):
            v = self.c_var(idx)
            if cons_i < len(constraints):
                self.s.add(Implies(v, constraints[cons_i]))
            else:
                print("soft cons. from group " + str(group) + " with index " + str(
                    cons_i) + "is out of range for constraints array")

    @staticmethod
    def get_id(x):
        return Z3_get_ast_id(x.ctx.ref(), x.as_ast())

    def c_var(self, i):
        if i not in self.varcache:
            v = Bool(self.c_prefix + str(abs(i)))
            self.idcache[self.get_id(v)] = abs(i)
            if i >= 0:
                self.varcache[i] = v
            else:
                self.varcache[i] = Not(v)
        return self.varcache[i]

    def check_subset(self, seed, improve_seed=False):
        assumptions = self.to_c_lits(seed)
        # print self.s
        # print "assumptions",assumptions
        is_sat = (self.s.check(assumptions) == sat)
        if improve_seed:
            if is_sat:
                # TODO: difficult to do efficiently...
                # seed = seed_from_model(solver.model(), n)
                pass
            else:
                seed = self.seed_from_core()
            return is_sat, seed
        else:
            return is_sat

    def to_c_lits(self, seed):
        return [self.c_var(i) for i in seed]

    def complement(self, aset):
        return set(range(self.n)).difference(aset)

    def seed_from_core(self):
        core = self.s.unsat_core()
        return [self.idcache[self.get_id(x)] for x in core]

    def shrink(self, seed, hard=[]):
        current = set(seed)
        for i in seed:
            if i not in current or i in hard:
                # May have been "also-removed"
                continue
            current.remove(i)
            if not self.check_subset(current):
                # Remove any also-removed constraints
                current = set(self.seed_from_core())
                pass
            else:
                current.add(i)
        return current

    def grow(self, seed, inplace):
        if inplace:
            current = seed
        else:
            current = seed[:]

        for i in self.complement(current):
            # if i in current:
            #    # May have been "also-satisfied"
            #    continue
            current.append(i)
            if self.check_subset(current):
                # Add any also-satisfied constraint
                # current = seed_from_model(s.model(), n)  # still too slow to help here
                pass
            else:
                current.pop()

        return current

