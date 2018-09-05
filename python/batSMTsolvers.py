import re
from collections import Counter
from collections import deque
from functools import reduce

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

    constraints = []
    # soft_constraints = defaultdict(list) #bat
    soft_constraints = []  # bat
    hard_constraints = []  # bat
    sizes = []  # bat
    assigned_to = []  # bat
    mutants = 0  # bat
    n = 0
    s = None
    varcache = {}
    idcache = {}
    assert_and_assume_constraints = []
    # var is mapped to the index of its assigning constraint, if exists
    assignment_map = {} # bat


    def __init__(self, filename, blocking_method):
        self.blocking_method = blocking_method
        self.read_constraints(filename)
        i = 0
        for c in self.constraints:
            # print i,c
            i = i + 1
        # print(self.soft_constraints)
        # print(self.hard_constraints)
        print("total cons:", len(self.constraints), "total hard+soft:", len(self.soft_constraints) + len(
            self.hard_constraints))
        # print(self.sizes)
        # print(self.n)
        # cons = self.constraints[0]
        # print [cons.arg(i) for i in range(cons.num_args())]
        # print cons.arg(0).children()
        self.mutants = reduce(lambda x, y: x * y, self.sizes)
        print("Total number of mutated programs:", self.mutants)
        self.make_solver()

    def read_constraints(self, filename):
        # if filename.endswith('.cnf'):
        #    self.constraints = read_dimacs(filename)
        # else:
        self.constraints = self.read_smt2(filename)
        self.read_group_smt2(filename)
        if (len(self.soft_constraints) == 0):
            print(
                "All constraints belong to group number {0}. For repair, add alternatives under a positive group number.")
            exit(0)
        self.soft_constraints = sorted(self.soft_constraints)
        self.sizes = [y for (x, y) in sorted(Counter(x for (x, y) in self.soft_constraints).items())]
        # self.n = sum(self.sizes)
        self.n = len(self.soft_constraints)

    def make_solver(self):
        self.s = Solver()
        for i in self.hard_constraints:
            if i < len(self.constraints):
                self.s.add(self.constraints[i])
            # print "adding" , i, self.constraints[i]
            else:
                print("hard cons. with index " + str(i) + " is out of range for constraints array")
        for idx, (group, cons_i) in enumerate(self.soft_constraints):
            v = self.c_var(idx)
            if cons_i < len(self.constraints):
                self.s.add(Implies(v, self.constraints[cons_i]))
            else:
                print("soft cons. from group " + str(group) + " with index " + str(
                    cons_i) + "is out of range for constraints array")

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
                        self.assert_and_assume_constraints.append(cons_i)
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
        print(self.assert_and_assume_constraints)
        print(self.assignment_map)
        f.close()

    def get_original_index(self, group):
        return next((idx, cons_i) for idx, (g, cons_i) in enumerate(self.soft_constraints) if g == group)

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

    # bat
    def get_bad_path(self, seed):
        var_a = Int('a')
        important_vars_queue = deque([str(var_a.decl())])
        important_vars_list = [str(var_a.decl())]
        res = set()
        while len(important_vars_queue) != 0:
            var = important_vars_queue.popleft()
            cons_i, dep_vars = self.get_dependent(var, seed)
            if cons_i not in self.hard_constraints:
                res.add(cons_i + 1)  # +1 bacuse cons_i is zero based
            for d_var in dep_vars:
                print(str(d_var), important_vars_list)
                if d_var not in important_vars_list:
                    important_vars_queue.append(d_var)
                    important_vars_list.append(d_var)
            print(important_vars_queue)
        return res

    # bat
    def get_dependent(self, var, seed):
        # assign_cons_list = self.assignment_list[var] #given the variable we have a list of constraints assigning to it
        # active_assign_cons_list = [c in assign_cons_list if c+1 in seed] #cons which are currently active according to seed
        # assert len(active_assign_cons_list) <= 1 #can't assign more than once in an SSA program. can be 0 if var is input
        # cons_i = len(active_assign_cons_list)==0 ? -1 : active_assign_cons_list[0]
        # variables = get_variables_from_expr(self.constraints[cons_i]) #get dependent variables from expr where cond is evaluated according to last given model
        # return 0, [str(var_a.decl())]
        return 0, "good"
