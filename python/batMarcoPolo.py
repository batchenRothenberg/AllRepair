try:
    import queue
except ImportError:
    import Queue as queue


class batMarcoPolo:
    def __init__(self, csolver, msolver, stats, config):
        self.subs = csolver
        self.map = msolver
        self.seeds = SeedManager(msolver, stats, config)
        self.stats = stats
        self.config = config
        self.bias_high = self.config['bias'] == 'MUSes'  # used frequently
        self.n = self.map.n  # number of constraints
        self.got_top = False  # track whether we've explored the complete set (top of the lattice)
        self.hard_constraints = []  # store hard clauses to be passed to shrink()
        self.i = 1  # bat

    def enumerate_basic(self):
        '''Basic MUS/MCS enumeration, as a simple reference/example.'''
        while True:
            with self.stats.time('seed'):
                seed = self.map.next_seed(self.stats)
                if seed is None:
                    return
            if self.config['verbose']:
                print
                ("- Program", str(self.i), "/", str(self.subs.mutants))
                print("Initial seed: %s" % " ".join([str(x + 1) for x in seed]))
                print
                ("Constraints of original code lines: " + self.map.original_vars)
                self.i = self.i + 1
                print
                (len(list(set([x + 1 for x in seed]) - set(self.map.original_vars))), "mutations")

            with self.stats.time('check'):
                res = self.subs.check_subset(seed)

            if res:  # subset is sat
                with self.stats.time('block'):
                    m = self.subs.s.model()
                    # print "aaaaa" , m
                    # print "prb:" , m["main::1::prb!0@1#2"]
                    # print "traversing model..."
                    # for d in m.decls():
                    #	print "%s = %s" % (d.name(), m[d])
                    # for c in self.subs.s.assertions():
                    #	print c
                    yield ("S", seed)
                    if self.config['smus']:
                        #print "seed is: ", [x for x in seed]
                        #bad_path_cons= self.subs.get_bad_path(seed)
                        #print "bad path is: ", [x for x in bad_path_cons]
                        #self.map.block_bad_repair(bad_path_cons)
                        #self.map.block_up(seed)
                        self.block_bad_repair(seed)
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
    def block_bad_repair(self, bad_path):
        # print "adding clause: ", [(-(x+1)) for x in bad_path]
        self.map.add_clause( [(-(x+1)) for x in bad_path] )
        if self.config['blockrepair']=="basic":
            pass
        elif self.config['blockrepair']=="slicing":
            print "slicing"
        elif self.config['blockrepair']=="generalization":
            print "generalization"

    def record_delta(self, name, oldlen, newlen, up):
        if up:
            assert newlen >= oldlen
            self.stats.add_stat("delta.%s.up" % name, float(newlen - oldlen) / self.n)
        else:
            assert newlen <= oldlen
            self.stats.add_stat("delta.%s.down" % name, float(oldlen - newlen) / self.n)

    def enumerate(self):
        '''MUS/MCS enumeration with all the bells and whistles...'''
        for seed, known_max in self.seeds:

            if self.config['verbose']:
                print("- Initial seed: %s" % " ".join([str(x + 1) for x in seed]))

            if self.config['maximize'] == 'always':
                assert not known_max
                with self.stats.time('maximize'):
                    oldlen = len(seed)
                    seed = self.map.maximize_seed(seed, direction=self.bias_high)
                    self.record_delta('max', oldlen, len(seed), self.bias_high)

                if self.config['verbose']:
                    print("- Maximized to: %s" % " ".join([str(x + 1) for x in seed]))

            with self.stats.time('check'):
                # subset check may improve upon seed w/ unsat_core or sat_subset
                oldlen = len(seed)
                seed_is_sat, seed = self.subs.check_subset(seed, improve_seed=True)
                self.record_delta('checkA', oldlen, len(seed), seed_is_sat)
                known_max = (known_max and (seed_is_sat == self.bias_high))

            if self.config['verbose']:
                print("- Seed is %s." % {True: "SAT", False: "UNSAT"}[seed_is_sat])
                if known_max:
                    print("- Seed is known to be optimal.")
                else:
                    print("- Seed improved by check: %s" % " ".join([str(x + 1) for x in seed]))

            # -m half: Only maximize if we're SAT and seeking MUSes or UNSAT and seeking MCSes
            if self.config['maximize'] == 'half' and (seed_is_sat == self.bias_high):
                assert not known_max
                # Maximize within Map and re-check satisfiability if needed
                with self.stats.time('maximize'):
                    oldlen = len(seed)
                    seed = self.map.maximize_seed(seed, direction=self.bias_high)
                    self.record_delta('max', oldlen, len(seed), self.bias_high)
                    known_max = True

                if self.config['verbose']:
                    print("- Half-maximization w/in map, new seed: %s" % " ".join([str(x + 1) for x in seed]))

                if len(seed) != oldlen:
                    # only need to re-check if maximization produced a different seed
                    with self.stats.time('check'):
                        # improve_seed set to True in case maximized seed needs to go in opposite
                        # direction of the maximization (i.e., UNSAT seed w/ MUS bias, SAT w/ MCS bias)
                        # (otherwise, no improvement is possible as we maximized it already)
                        oldlen = len(seed)
                        seed_is_sat, seed = self.subs.check_subset(seed, improve_seed=True)
                        self.record_delta('checkB', oldlen, len(seed), seed_is_sat)
                        known_max = (len(seed) == oldlen and seed_is_sat == self.bias_high)

                    if self.config['verbose']:
                        print("- Half-max check: Seed is %s" % {True: "SAT", False: "UNSAT"}[seed_is_sat])
                        if known_max:
                            print("- Seed is known to be optimal.")
                        else:
                            print("- Half-max check: Seed improved by check: %s" % " ".join([str(x + 1) for x in seed]))
                else:  # no re-check needed
                    if self.config['verbose']:
                        print("- Seed is known to be optimal.")

            if seed_is_sat:
                if known_max:
                    MSS = seed
                else:
                    with self.stats.time('grow'):
                        oldlen = len(seed)
                        MSS = self.subs.grow(seed, inplace=True)
                        self.record_delta('grow', oldlen, len(MSS), True)

                    if self.config['verbose']:
                        print("- Grow() -> MSS")

                with self.stats.time('block'):
                    yield ("S", MSS)
                    self.map.block_down(MSS)
                    if self.config['block_both'] and not self.bias_high:
                        self.map.block_up(MSS)

                if self.config['verbose']:
                    print("- MSS blocked.")

                if self.config['mssguided']:
                    with self.stats.time('mssguided'):
                        # don't check parents if parent is top and we've already seen it (common)
                        if len(MSS) < self.n - 1 or not self.got_top:
                            # add any unexplored superset to the queue
                            newseed = self.map.find_above(MSS)
                            if newseed:
                                self.seeds.add_seed(newseed, False)
                                if self.config['verbose']:
                                    print("- New seed found above MSS: %s" % " ".join([(x + 1) for x in seed]))

            else:  # seed is not SAT
                self.got_top = True  # any unsat set covers the top of the lattice
                if known_max:
                    MUS = seed
                else:
                    if self.config['use_implies']:
                        # This might change after every blocking clause,
                        # but we only need to check right before we're going to use them.
                        implies = self.map.solver.implies()
                        self.hard_constraints = [x - 1 for x in implies if x > 0]

                    with self.stats.time('shrink'):
                        oldlen = len(seed)
                        self.stats.add_stat("hard_constraints", len(self.hard_constraints))
                        MUS = self.subs.shrink(seed, hard=self.hard_constraints)
                        self.record_delta('shrink', oldlen, len(MUS), False)

                    if self.config['verbose']:
                        print("- Shrink() -> MUS")

                with self.stats.time('block'):
                    yield ("U", MUS)
                    self.map.block_up(MUS)
                    if self.config['block_both'] and self.bias_high:
                        self.map.block_down(MUS)
                    if self.config['smus']:
                        self.map.block_down(MUS)
                        self.map.block_above_size(len(MUS) - 1)

                if self.config['verbose']:
                    print("- MUS blocked.")


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
