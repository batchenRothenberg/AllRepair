from pyminisolvers import minisolvers


class MapSolver:
    """The base class for any MapSolver, implementing common utility functions."""

    def __init__(self, sizes, bias=True, dump=None):  # bat
        """Common initialization.

        Args:
            n: The number of constraints to map.
            bias: Boolean specifying the solver's bias.  True is a
                  high/inclusion/MUS bias; False is a low/exclusion/MSS bias;
                  None is no bias.
        """
        self.n = sum(sizes)
        self.sizes = sizes  # bat
        self.bias = bias
        self.all_n = set(range(self.n))  # used in complement fairly frequently #bat
        self.dump = dump

    def check_seed(self, seed):
        """Check whether a given seed is still unexplored.

        Returns:
            True if seed is unexplored (i.e., its corresponding assignment is a model)
        """
        out = self.complement(seed)
        return self.solver.solve([(i + 1) for i in seed] + [-(i + 1) for i in out])

    def find_above(self, seed):
        """Look for and return any unexplored point including the given seed.
            Calling map.find_above(MSS) after map.block_down(MSS) will thus find
            strict supersets of the MSS, as the MSS itself has been blocked.

        Returns:
            Any unexplored strict superset of seed, if one exists.
        """
        superset_exists = self.solver.solve((i + 1) for i in seed)
        if superset_exists:
            return self.get_seed()
        else:
            return None

    def get_seed(self):
        """Get the seed from the current model.  (Depends on work in next_seed to be valid.)

        Returns:
            A seed as an array of 0-based constraint indexes.
        """
        return self.solver.get_model_trues(start=0, end=self.n)

        # slower:
        # model = self.solver.get_model()
        # return [i for i in range(self.n) if model[i]]

        # slowest:
        # seed = []
        # for i in range(self.n):
        #    if self.solver.model_value(i+1):
        #        seed.add(i)
        # return seed

    def maximize_seed(self, seed, direction):
        """Maximize a given seed within the current set of constraints.
           The Boolean direction parameter specifies up (True) or down (False)

        Returns:
            A seed as an array of 0-based constraint indexes.
        """
        while True:
            comp = self.complement(seed)
            x = self.solver.new_var() + 1
            if direction:
                # search for a solution w/ all of the current seed plus at
                # least one from the current complement.
                self.solver.add_clause([-x] + [i + 1 for i in comp])  # temporary clause
                # activate the temporary clause and all seed clauses
                havenew = self.solver.solve([x] + [i + 1 for i in seed])
            else:
                # search for a solution w/ none of current complement and at
                # least one from the current seed removed.
                self.solver.add_clause([-x] + [-(i + 1) for i in seed])  # temporary clause
                # activate the temporary clause and deactivate complement clauses
                havenew = self.solver.solve([x] + [-(i + 1) for i in comp])
            self.solver.add_clause([-x])  # remove the temporary clause

            if havenew:
                seed = self.get_seed()
            else:
                return seed

    def complement(self, aset):
        """Return the complement of a given set w.r.t. the set of mapped constraints."""
        return self.all_n.difference(aset)

    def add_clause(self, clause):
        """Add a given clause to the Map solver."""
        self.solver.add_clause(clause)
        if self.dump is not None:
            self.dump.write(" ".join(map(str, clause)) + " 0\n")

    def block_down(self, frompoint):
        """Block down from a given set."""
        comp = self.complement(frompoint)
        clause = [(i + 1) for i in comp]
        self.add_clause(clause)

    def block_up(self, frompoint):
        """Block up from a given set."""
        clause = [-(i + 1) for i in frompoint]
        self.add_clause(clause)

    # bat
    def block_good_repair(self, seed):
        # print "seed: " + str(seed)
        # print "original: " + str([self.original_vars])
        # self.solver.add_clause( [(x) for x in self.original_vars if x-1 not in seed] ) #bad because it blocks *all* changes to changed lines, instead of the specific changes made.
        return [(-(x + 1)) for x in seed if x + 1 not in self.original_vars]


class MinicardMapSolver(MapSolver):
    def __init__(self, sizes, bias=True,
                 limit=None):  # bat # bias=True is a high/inclusion/MUS bias; False is a low/exclusion/MSS bias.
        MapSolver.__init__(self, sizes, bias)

        self.m = len(sizes)  # num of groups- used frequently
        self.n = sum(sizes)  # num of total cons - used frequently
        self.k = self.m  # initial lower bound on # of unfixed lines (True variables of original cons.)
        self.limit = limit  # bat

        self.solver = minisolvers.MinicardSolver()
        # while self.solver.nvars() < self.n:
        #   self.solver.new_var(self.bias)
        self.original_vars = []
        start = 1
        for size in sizes:
            self.original_vars.append(start)
            self.solver.new_var(True)  # original variable
            self.solver.new_vars(size - 1, False)  # repair variables
            self.solver.add_atmost(range(start, start + size), 1)  # at most one cons from each group
            self.solver.add_clause(
                range(start, start + size))  # at least one cons from each group => only legal programs are considered
            start = start + size
        # print self.sizes
        # print self.original_vars

        # add "bound-setting" variables
        for i in range(self.m):
            self.solver.new_var()

        # add cardinality constraint (comment is for high bias, maximal model;
        #                             becomes AtMostK for low bias, minimal model)
        # want: generic AtLeastK over all n variables
        # how: make AtLeast([n vars, n bound-setting vars], n)
        #      then, assume the desired k out of the n bound-setting vars.
        # e.g.: for real vars a,b,c: AtLeast([a,b,c, x,y,z], 3)
        #       for AtLeast 3: assume(-x,-y,-z)
        #       for AtLeast 1: assume(-x)
        # and to make AtLeast into an AtMost:
        #   AtLeast([lits], k) ==> AtMost([-lits], #lits-k)
        # if self.bias:
        self.solver.add_atmost([-(x) for x in self.original_vars] + [-(self.n + x + 1) for x in range(self.m)], self.m)
        # else:
        #   self.solver.add_atmost([(x+1) for x in range(self.n * 2)], self.n)

    def solve_with_bound(self, k):
        # same assumptions work both for high bias / atleast and for low bias / atmost
        return self.solver.solve(
            [-(self.n + x + 1) for x in range(k)] + [(self.n + k + x + 1) for x in range(self.m - k)])

    def next_seed(self, stats):
        '''
            Find the next *maximum* model.
        '''
        if self.solve_with_bound(self.k):
            return self.get_seed()

        # if self.bias:
        if not self.solve_with_bound(0):
            # no more models
            stats.size = self.m  # record max reviewed size as max size
            return None
        # move to the next bound
        self.increase_mutation_size(stats)
        if self.limit is not None and self.m - self.k > self.limit:
            print("Mutation size limit reached")
            exit(5)
        # else:
        #   if not self.solve_with_bound(self.n):
        #        # no more models
        #        return None
        #    # move to the next bound
        #    self.k += 1

        while not self.solve_with_bound(self.k):
            # if self.bias:
            self.increase_mutation_size(stats)
            if self.limit is not None and self.m - self.k > self.limit:
                print("Mutation size limit reached")
                exit(5)
            # else:
            #    self.k += 1

        assert 0 <= self.k <= self.n

        return self.get_seed()

    def increase_mutation_size(self, stats):
        stats.size = self.m - self.k  # record max reviewed size
        print("Time to cover search space up to size "+str(self.m - self.k)+": %.3f" % stats.current_time())
        self.k -= 1

    def block_above_size(self, size):
        self.solver.add_atmost([(x + 1) for x in range(self.n)], size)
        self.k = min(size, self.k)

    def block_below_size(self, size):
        self.solver.add_atmost([-(x + 1) for x in range(self.n)], self.n - size)
        self.k = min(size, self.k)


class MinisatMapSolver(MapSolver):
    def __init__(self, sizes, bias=True,
                 dump=None):  # bias=True is a high/inclusion/MUS bias; False is a low/exclusion/MSS bias; None is no bias.
        MapSolver.__init__(self, sizes, bias, dump)

        self.solver = minisolvers.MinicardSolver()  # bat minicard instead of minisat
        # while self.solver.nvars() < self.n:
        #    self.solver.new_var(self.bias)

        # bat
        start = 1
        for size in sizes:
            self.solver.new_var(True)
            self.solver.new_vars(size - 1, False)
            # print(range(start,start+size))
            self.solver.add_atmost(range(start, start + size), 1)
            self.solver.add_clause(range(start, start + size))
            start = start + size

        # if self.bias is None:
        #    self.solver.set_rnd_pol(True)

    def next_seed(self):
        if self.solver.solve():
            return self.get_seed()
        else:
            return None
