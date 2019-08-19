from InGeneer import generalizer
from InGeneer import precise_domain
from InGeneer import interval_domain
from InGeneer import formula_strengthener

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
            with self.stats.time('SAT check'):
                seed = self.map.next_seed(self.stats)
                if seed is None:
                    return
                self.multi_program.sat_seed = seed
                if self.config['verbose']:
                    print("- Program " + str(self.i) + "/" + str(self.multi_program.mutants))
                    print("Initial seed: %s" % " ".join([str(x + 1) for x in seed]))
                    print("Constraints of original code lines: " + str(self.map.original_vars))
                    self.i = self.i + 1
                    print(str(len(list(set([x + 1 for x in seed]) - set(self.map.original_vars)))) + " mutations")

            # To print all times add verbose=True
            with self.stats.time('SMT check'):
                res = self.subs.check_subset(seed)

            if res:  # subset is sat
                with self.stats.time('SAT block'):
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
                        assert not self.map.solver.solve([x+1 for x in seed])
                    else:
                        self.map.block_up(
                            seed)  # block_up/down have the same effect- block only seed (since we are looking at fixed size subsets)
            else:  # subset is unsat
                with self.stats.time('SAT block'):
                    # check if "repair" is in fact the original program
                    if self.map.k == self.map.m:
                        print ("Original program is correct. No need for repair.")
                        exit(8)
                    yield ("U", seed)
                    if self.config['smus']:
                        clause = self.map.block_good_repair(seed)
                        # print "block good repair"
                        self.map.solver.add_clause(clause)
                    else:
                        self.map.block_up(seed) #block_up/down have the same effect- block only seed (since we are looking at fixed size subsets)

    #bat
    def block_bad_repair(self, seed):
        # print("seed: ", str(seed))
        if self.config['blockrepair']=="basic":
            return [(-(x + 1)) for x in seed]
        else:
            roots = self.multi_program.get_root_variables()
            if self.config['blockrepair']=="slicing":
                # print("slicing")
                trace_literals = []
                self.multi_program.postorder(roots, self.multi_program.append_literal(trace_literals))
                literals = self.multi_program.get_selected_literals_from_list(trace_literals)
                # print("literals: "+str(literals))
                return [(-(x + 1)) for x in literals]
            elif self.config['blockrepair']=="generalization":
                # print("generalization")
                trace = []
                self.multi_program.postorder(roots, self.multi_program.append_transition(trace))
                DOMAIN_STR = "intervals"
                DEBUG = False
                mt = self.multi_program.get_multitrace_from_trace(trace)
                smt_model = self.multi_program.smt_model
                # print("mt: "+str(mt))
                if DOMAIN_STR == "precise_no_simplify":
                    domain = precise_domain.PreciseDomain(simplification=False)
                    initial_formula = self.multi_program.get_initial_formula_from_demands()
                elif DOMAIN_STR == "precise_with_simplify":
                    domain = precise_domain.PreciseDomain(simplification=True)
                    initial_formula = self.multi_program.get_initial_formula_from_demands()
                elif DOMAIN_STR == "intervals":
                    domain = interval_domain.IntervalDomain(debug=True)
                    initial_formula = self.multi_program.get_initial_formula_from_demands()
                    initial_formula = formula_strengthener.strengthen(initial_formula,smt_model)
                else:
                    assert False
                gen = generalizer.Generalizer(domain,debug=DEBUG)
                good_stmts_set = gen.generalize_trace(mt, initial_formula, model=smt_model, print_annotation=False)
                literals = set([st.literal for st in good_stmts_set if st.literal is not None])
                # print(literals)
                return [(x + 1) for x in literals]

    @staticmethod
    def index0(list):
        def insert_in_0(v):
            list.insert(0, v)
        return insert_in_0

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
