"""Utility class(es) for marco_py"""
import time
from abc import ABCMeta, abstractmethod
from collections import Counter, defaultdict
from z3 import *

# Three options for measuring time: choose one.
# TODO: Consider using time.process_time() (only in 3.3, though)
_get_time = time.time  # wall-time


# time.clock() is not portable - behaves differently per OS
# _get_time = time.clock   # user-time

# import os
# _get_time = lambda: sum(os.times()[:4])  # combined user/sys time for this process and its children


class Statistics:
    def __init__(self):
        self._start = _get_time()
        self._times = Counter()
        self._counts = Counter()
        self._stats = defaultdict(list)
        self._category = None
        self.size = 0  # bat

    # Usage:
    #  s = Statistics()
    #  with s.time("one")
    #    # do first thing
    #  with s.time("two")
    #    # do second thing
    def time(self, category):
        self._category = category
        return self.Timer(self)

    # Context manager class for time() method
    class Timer:
        def __init__(self, stats):
            self._stats = stats

        def __enter__(self):
            self._stats.start_time()

        def __exit__(self, ex_type, ex_value, traceback):
            self._stats.end_time()
            return False  # doesn't handle any exceptions itself

    def start_time(self):
        self._counts[self._category] += 1
        self._curr = _get_time()

    def end_time(self):
        self._times[self._category] += _get_time() - self._curr
        self._category = None

    def current_time(self):
        return _get_time() - self._start

    def get_times(self):
        self._times['total'] = self.current_time()
        if self._category:
            # If we're in a category currently,
            # give it the time up to this point.
            self._times[self._category] += _get_time() - self._curr

        return self._times

    def get_counts(self):
        return self._counts

    def add_stat(self, name, value):
        self._stats[name].append(value)

    def get_stats(self):
        return self._stats


class Graph():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_children(self, v):
        pass

    def _postorder_aux(self, v, do_something, visited):
        visited.append(v)
        for c in self.get_children(v):
            if c not in visited:
                self._postorder_aux(c, do_something, visited)
        do_something(v)

    def postorder(self, roots, do_something):
        """
        Applies do_something to every node in the subgraph of roots,
        with the guarantee that every node will be processed after all of its children.
        :param v:
        :param do_something:
        :return:
        """
        visited = []
        for r in roots:
            self._postorder_aux(r, do_something, visited)

def is_If(z3_expr):
    return str(z3_expr.decl()) == "If"

######################################################################################################
#   Following functions are copy-pasted from z3util.py latest version on Github,
#   in order to avoid a dependency on a missing file (common.py)
######################################################################################################

def vset(seq, idfun=None, as_list=True):
    # This functions preserves the order of arguments while removing duplicates.
    # This function is from https://code.google.com/p/common-python-vu/source/browse/vu_common.py
    # (Thanhu's personal code). It has been copied here to avoid a dependency on vu_common.py.
    """
    order preserving
    >>> vset([[11,2],1, [10,['9',1]],2, 1, [11,2],[3,3],[10,99],1,[10,['9',1]]],idfun=repr)
    [[11, 2], 1, [10, ['9', 1]], 2, [3, 3], [10, 99]]
    """

    def _uniq_normal(seq):
        d_ = {}
        for s in seq:
            if s not in d_:
                d_[s] = None
                yield s

    def _uniq_idfun(seq, idfun):
        d_ = {}
        for s in seq:
            h_ = idfun(s)
            if h_ not in d_:
                d_[h_] = None
                yield s

    if idfun is None:
        res = _uniq_normal(seq)
    else:
        res = _uniq_idfun(seq, idfun)


    return list(res) if as_list else res

def get_vars(f,rs=[]):
    """
    >>> x,y = Ints('x y')
    >>> a,b = Bools('a b')
    >>> get_vars(Implies(And(x+y==0,x*2==10),Or(a,Implies(a,b==False))))
    [x, y, a, b]
    """
    if __debug__:
        assert is_expr(f)

    if is_const(f):
        if is_expr_val(f):
            return rs
        else:  #variable
            return vset(rs + [f],str)

    else:
        for f_ in f.children():
            rs = get_vars(f_,rs)

        return vset(rs,str)

def get_vars_as_string(f,rs=[]):
    return [str(v) for v in get_vars(f,rs)]

def is_expr_val(v):
    """
    EXAMPLES:
    >>> is_expr_val(Int('7'))
    False
    >>> is_expr_val(IntVal('7'))
    True
    >>> is_expr_val(Bool('y'))
    False
    >>> is_expr_val(Int('x') + 7 == Int('y'))
    False
    >>> LOnOff, (On,Off) = EnumSort("LOnOff",['On','Off'])
    >>> Block,Reset,SafetyInjection=Consts("Block Reset SafetyInjection",LOnOff)
    >>> is_expr_val(LOnOff)
    False
    >>> is_expr_val(On)
    True
    >>> is_expr_val(Block)
    False
    >>> is_expr_val(SafetyInjection)
    False
    """
    return is_const(v) and v.decl().kind()!=Z3_OP_UNINTERPRETED

def parse_If(if_expr, model):
    assert is_If(if_expr)
    guard = if_expr.arg(0)
    true_expr = if_expr.arg(1)
    false_expr = if_expr.arg(2)
    if is_true(model.evaluate(guard)):
        return True , true_expr
    else:
        return False, false_expr

######################################################################################################
#   Following functions are copy-pasted from z3util.py latest version on Github,
#   in order to avoid a dependency on a missing file (common.py)
######################################################################################################

def vset(seq, idfun=None, as_list=True):
    # This functions preserves the order of arguments while removing duplicates.
    # This function is from https://code.google.com/p/common-python-vu/source/browse/vu_common.py
    # (Thanhu's personal code). It has been copied here to avoid a dependency on vu_common.py.
    """
    order preserving
    >>> vset([[11,2],1, [10,['9',1]],2, 1, [11,2],[3,3],[10,99],1,[10,['9',1]]],idfun=repr)
    [[11, 2], 1, [10, ['9', 1]], 2, [3, 3], [10, 99]]
    """

    def _uniq_normal(seq):
        d_ = {}
        for s in seq:
            if s not in d_:
                d_[s] = None
                yield s

    def _uniq_idfun(seq, idfun):
        d_ = {}
        for s in seq:
            h_ = idfun(s)
            if h_ not in d_:
                d_[h_] = None
                yield s

    if idfun is None:
        res = _uniq_normal(seq)
    else:
        res = _uniq_idfun(seq, idfun)


    return list(res) if as_list else res

def get_vars(f,rs=[]):
    """
    >>> x,y = Ints('x y')
    >>> a,b = Bools('a b')
    >>> get_vars(Implies(And(x+y==0,x*2==10),Or(a,Implies(a,b==False))))
    [x, y, a, b]
    """
    if __debug__:
        assert is_expr(f)

    if is_const(f):
        if is_expr_val(f):
            return rs
        else:  #variable
            return vset(rs + [f],str)

    else:
        for f_ in f.children():
            rs = get_vars(f_,rs)

        return vset(rs,str)

def is_expr_val(v):
    """
    EXAMPLES:
    >>> is_expr_val(Int('7'))
    False
    >>> is_expr_val(IntVal('7'))
    True
    >>> is_expr_val(Bool('y'))
    False
    >>> is_expr_val(Int('x') + 7 == Int('y'))
    False
    >>> LOnOff, (On,Off) = EnumSort("LOnOff",['On','Off'])
    >>> Block,Reset,SafetyInjection=Consts("Block Reset SafetyInjection",LOnOff)
    >>> is_expr_val(LOnOff)
    False
    >>> is_expr_val(On)
    True
    >>> is_expr_val(Block)
    False
    >>> is_expr_val(SafetyInjection)
    False
    """
    return is_const(v) and v.decl().kind()!=Z3_OP_UNINTERPRETED