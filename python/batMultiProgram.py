from collections import Counter
from functools import reduce
from z3 import *

from InGeneer import stmt
from InGeneer.z3_utils import evaluate_phi_function
from batutils import Graph, get_vars_as_keys, is_If, parse_If, findall_regular_expression, MyGraph
from InGeneer.formula_strengthener import nnf_simplify,remove_or


class batMultiProgram(Graph):

    constraints = []
    soft_constraints = []
    hard_constraints = []
    # var is mapped to the index of its assigning constraint, if exists
    assignment_map = {}
    sizes = []
    n = 0
    mutants = 0
    sat_seed = None     # Determines the chosen program
    smt_model = None    # Determines the chosen path within the program, leading to a bug.
    demands_formula = None
    group_info_map = {} # Maps a positive group number to a string with its file location and line number

    def __init__(self, filename, blocking_method):
        self.blocking_method = blocking_method
        self.read_constraints(filename)
        number_of_constraints = len(self.constraints)
        number_of_hard_constraints = len(self.hard_constraints)
        number_of_soft_constraints = len(self.soft_constraints)
        if number_of_constraints != (number_of_hard_constraints + number_of_soft_constraints):
            print("Gsmt2 parsing error: Some constraints do not belong to any group.")
            print("Make sure every constraint ends with a comment of the form ';Group-num {n}'")
            exit(1)
        self.mutants = reduce(lambda x, y: x * y, self.sizes)
        print("Hard constraints (group 0): "+str(number_of_hard_constraints))
        print("Max mutation size: "+str(len(self.sizes)))
        print("Mutated programs in search space: "+str(self.mutants))

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
        soft_i = 0
        demand_constraints = []
        for line in f.readlines():
            res = findall_regular_expression(';Group-number *\{([0-9,a-z]*)\}', line)
            if res:
                # add constraint to hard/soft constraints
                if res[0] == '0' or res[0] == 'demand':
                    self.hard_constraints.append(cons_i)
                else:
                    self.soft_constraints.append((int(res[0]), cons_i))
                    self.parse_and_save_location_information(int(res[0]), line)
                    soft_i = soft_i + 1
                # if assert or assume - add to assert_and_assume list. Otherwise - it's an assignment, add to map.
                if self.blocking_method != "basic":
                    if res[0] == 'demand':
                        demand_constraints.append(cons_i)
                    else:
                        cons = self.constraints[cons_i]
                        if is_and(cons): # compound constraint due to loop unwinding
                            assigns = cons.children()
                        else:
                            assigns = [cons]
                        for ass in assigns:
                            assert is_eq(ass)
                            assert ass.num_args() > 1
                            # Add to assignment map only if not already in:
                            # makes sure each variable is mapped to its first assignment, i.e., the assignment in the original program
                            lhs = ass.arg(0)
                            rhs = ass.arg(1)
                            lhs_key = lhs.get_id()
                            if lhs_key not in self.assignment_map:
                                # print_var_to_key_map(lhs)
                                if res[0] == '0': # phi-function or hard constraint that is not an assert or assume (e.g., cbmc init)
                                    if is_If(rhs):  # phi-function assignment
                                        guard = rhs.arg(0)
                                        true_var = rhs.arg(1)
                                        false_var = rhs.arg(2)
                                        self.assignment_map[lhs_key] = (None, PhiFunction(guard,true_var,false_var))
                                    else:  # standard assignment
                                        self.assignment_map[lhs_key] = (None, get_vars_as_keys(rhs))
                                else: # soft constraint
                                    self.assignment_map[lhs_key] = (soft_i-1, get_vars_as_keys(rhs)) # soft_i was already increased
                cons_i = cons_i + 1
        self.demands_formula = And([nnf_simplify(self.constraints[i]) for i in demand_constraints])
        # self.debug_dependency_graph()
        f.close()

    @staticmethod
    def print_var_to_key_map(lhs):
        print(str(lhs) + ": " + str(lhs.get_id()))

    def debug_dependency_graph(self):
        graph_map = {}
        for key in self.assignment_map:
            value = self.assignment_map[key][1]
            # print (str(key)+" -> "+str(value))
            if isinstance(value, PhiFunction):
                graph_map[key] = [value.guard.get_id(), value.true_var.get_id(), value.false_var.get_id()]
            else:
                graph_map[key] = value
        dependency_grpah = MyGraph(graph_map)
        print(dependency_grpah.find_path(657,
                                         363))  # [657, 640L, 590L, 574L, 575L, 586L, 550L, 547L, 525L, 513L, 477L, 478L, 384L]
        print(dependency_grpah.find_path(478, 150))
        print(dependency_grpah.find_path(478, 381))
        print(dependency_grpah.find_path(381, 150))  # [381, 361L, 359L, 150L]

    def parse_and_save_location_information(self, groupnum, line):
        if groupnum not in self.group_info_map.keys():
            res = findall_regular_expression('Group-info *\{(.*)\}', line)
            if not res:
                info = "<location unavailable>"
            else:
                info = res[0]
            self.group_info_map[groupnum] = info

    def get_original_index(self, group):
        return next((idx, cons_i) for idx, (g, cons_i) in enumerate(self.soft_constraints) if g == group)

    def get_children(self, variable_key):
        if variable_key in self.assignment_map:
            literal, object = self.assignment_map[variable_key]
            if isinstance(object,PhiFunction):
                chosen_var = evaluate_phi_function(object, self.smt_model)
                guard_var_keys = get_vars_as_keys(object.guard)
                chosen_var_keys = get_vars_as_keys(chosen_var)
                return list(set(guard_var_keys) | set(chosen_var_keys))
            elif isinstance(object,list):
                return object
            else:
                return False
        else:
            return []

    @staticmethod
    def unwind_cons(cons, v):
        if is_and(cons):  # cons is the result of loop/function unwinding. Find the assignment to v in it.
            for child in cons.children():
                assert is_eq(child)
                if child.arg(0).get_id() == v:
                    return child
        else:  # cons is an assignment (phi-function, condition or standard assignment)
            assert is_eq(cons)
            return cons

    def append_transition(self, list):
        #
        def append_correct_transition_at_0(var):
            if var in self.assignment_map.keys():
                transition = self.assignment_map[var]
                expr = transition.expr
                assert is_eq(expr)
                lhs = expr.arg(0)
                rhs = expr.arg(1)
                if is_If(rhs):
                    evaluation, chosen_var = parse_If(rhs, self.smt_model)
                    transition = DependencyTransition(None, lhs == chosen_var)
                list.insert(0, transition)
        #
        return append_correct_transition_at_0

    def append_literal(self, list):
        #
        def append_literal_at_0(var):
            if var in self.assignment_map.keys():
                literal, object = self.assignment_map[var]
                list.insert(0, literal)
        #
        return append_literal_at_0

    def get_selected_literals_from_list(self, literal_list):
        res = set()
        for lit in literal_list:
            if lit is not None:
                selected_literal = self.replace_literal_with_selected_literal(lit)
                res.add(selected_literal)
        return res

    def replace_literal_with_selected_literal(self, literal):
        while literal not in self.sat_seed:
            literal = literal + 1
        return literal

    def get_root_variables(self):
        demands_formula_no_or = self.get_initial_formula_from_demands()
        return get_vars_as_keys(demands_formula_no_or)

    def get_initial_formula_from_demands(self):
        return remove_or(self.demands_formula, self.smt_model)

    def get_multitrace_from_trace(self, trace):
        res = []
        for transition in trace:
            if transition.is_phi():
                t_1, t_2 = self.split_phi_transition(transition)
                res.append([t_1])
                res.append([t_2])
            elif transition.is_soft():
                l = self.get_all_transitions_of_group(transition)
                res.append(l)
            else: # transition is hard (possibly due to CBMC init)
                res.append([transition])
        return res

    def split_phi_transition(self, transition):
        assert transition.is_phi()
        expr = transition.expr
        t_1 = DependencyTransition(None,expr.arg(0))
        t_2 = DependencyTransition(None,expr.arg(1))
        return t_1, t_2

    def get_all_transitions_of_group(self, transition):
        soft_index = transition.literal
        soft_len = len(self.soft_constraints)
        assert soft_index >= 0 and soft_index < soft_len
        res = [transition]
        group_num, cons_index = self.soft_constraints[soft_index]
        assert transition.is_assignment()
        assigned_var = transition.expr.arg(0)
        while soft_index + 1 < soft_len:
            soft_index += 1
            new_group_num, new_cons_index = self.soft_constraints[soft_index]
            if new_group_num == group_num:
                t = DependencyTransition(soft_index, self.unwind_cons(self.constraints[new_cons_index],assigned_var.get_id()))
                res.append(t)
        return res


class PhiFunction:
    def __init__(self, guard, true_var, false_var):
        self.guard = guard
        self.true_var = true_var
        self.false_var = false_var

    def __str__(self):
        return "["+str(self.guard.get_id())+", "+str(self.true_var.get_id())+", "+str(self.false_var.get_id())+"]"

    def __repr__(self):
        return str(self)


class DependencyTransition(stmt.Stmt):

    def __init__(self, literal, expr):
        self.literal = literal
        super(DependencyTransition, self).__init__(expr)
        if self.is_assignment():
            self.lhs = self.expr.arg(0)
            self.rhs = self.expr.arg(1)
        else:
            self.lhs = None
            self.rhs = None

    def __str__(self):
        if self.is_assignment():
            assign_stmt = stmt.AssignmentStmt(self.expr)
            return "(" + str(self.literal) + ": " + str(assign_stmt) + ") "
        else:
            return "(" + str(self.literal) + ": " + str(self.expr) + ") "

    def __repr__(self):
        return str(self)

    def is_assignment(self):
        return is_eq(self.expr)

    def is_condition(self):
        return not self.is_assignment()

    def is_phi(self):
        return is_and(self.expr)

    def is_soft(self):
        return not self.literal is None
