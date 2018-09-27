try:
    import queue
except ImportError:
    import Queue as queue
from batSlicing import *

class batMarcoPolo:
    def __init__(self, csolver, msolver, stats, config, multi_program):
        self.subs = csolver
        self.map = msolver
        self.seeds = SeedManager(msolver, stats, config)
        self.stats = stats
        self.config = config
        self.multi_program = multi_program
        self.bias_high = self.config['bias'] == 'MUSes'  # used frequently
        self.n = self.map.n  # number of constraints
        self.got_top = False  # track whether we've explored the complete set (top of the lattice)
        self.i = 1  # bat

    def enumerate_basic(self):
        '''Basic MUS/MCS enumeration, as a simple reference/example.'''
        while True:
            with self.stats.time('seed'):
                seed = self.map.next_seed(self.stats)
                if seed is None:
                    return
                self.multi_program.sat_seed = seed
                if self.config['verbose']:
                    print("- Program", str(self.i), "/", str(self.subs.mutants))
                    print("Initial seed: %s" % " ".join([str(x + 1) for x in seed]))
                    print("Constraints of original code lines: " + self.map.original_vars)
                    self.i = self.i + 1
                    print(len(list(set([x + 1 for x in seed]) - set(self.map.original_vars))), "mutations")

            with self.stats.time('check'):
                res = self.subs.check_subset(seed)

            if res:  # subset is sat
                with self.stats.time('block'):
                    # print "aaaaa" , m
                    # print "prb:" , m["main::1::prb!0@1#2"]
                    # print "traversing model..."
                    # for d in m.decls():
                    #	print "%s = %s" % (d.name(), m[d])
                    # for c in self.subs.s.assertions():
                    #	print c
                    yield ("S", seed)
                    self.multi_program.smt_model = self.subs.s.model()
                    if self.config['smus']:
                        clause = self.block_bad_repair(seed)
                        # print("blocking: ", clause)
                        self.map.solver.add_clause(clause)
                    else:
                        self.map.block_up(
                            seed)  # block_up/down have the same effect- block only seed (since we are looking at fixed size subsets)
            else:  # subset is unsat
                with self.stats.time('block'):
                    yield ("U", seed)
                    if self.config['smus']:
                        self.map.block_good_repair(seed)
                        # print "block good repair"
                    else:
                        self.map.block_up(seed) #block_up/down have the same effect- block only seed (since we are looking at fixed size subsets)

    #bat
    def block_bad_repair(self, seed):
        if self.config['blockrepair']=="basic":
            return [(-(x + 1)) for x in seed]
        elif self.config['blockrepair']=="slicing":
            print("slicing")
            return slice_program(seed, self.subs.s.model(), self.multi_program.demand_constraints, self.multi_program.constraints, self.multi_program.assignment_map, self.multi_program.soft_constraints)
        elif self.config['blockrepair']=="generalization":
            print("generalization")
            roots = self.multi_program.get_root_variables()
            var_list = []
            self.multi_program.postorder(roots, var_list.append)
            print(var_list)
            return [(-(x + 1)) for x in seed]

    def print_aux(self, v):
        print(v)

    def record_delta(self, name, oldlen, newlen, up):
        if up:
            assert newlen >= oldlen
            self.stats.add_stat("delta.%s.up" % name, float(newlen - oldlen) / self.n)
        else:
            assert newlen <= oldlen
            self.stats.add_stat("delta.%s.down" % name, float(oldlen - newlen) / self.n)


class SeedManager:
    def __init__(self, msolver, stats, config):
        self.map = msolver
        self.stats = stats
        self.config = config
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        with self.stats.time('seed'):
            if not self.queue.empty():
                return self.queue.get()
            else:
                seed, known_max = self.seed_from_solver()
                if seed is None:
                    raise StopIteration
                return seed, known_max

    def add_seed(self, seed, known_max):
        self.queue.put((seed, known_max))

    def seed_from_solver(self):
        known_max = (self.config['maximize'] == 'solver')
        return self.map.next_seed(), known_max

    # for python 2 compatibility
    next = __next__
