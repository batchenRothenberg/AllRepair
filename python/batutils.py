"""Utility class(es) for marco_py"""
import cProfile, pstats, io, re
import StringIO
import time
import re
from abc import ABCMeta, abstractmethod
from collections import Counter, defaultdict
from z3 import *

# Three options for measuring time: choose one.
# TODO: Consider using time.process_time() (only in 3.3, though)
from InGeneer.z3_utils import get_id

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
        self._verbose = False

    # Usage:
    #  s = Statistics()
    #  with s.time("one")
    #    # do first thing
    #  with s.time("two")
    #    # do second thing
    def time(self, category, verbose=False):
        self._category = category
        self._verbose = verbose
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
        calculated_time = _get_time() - self._curr
        self._times[self._category] += calculated_time
        if self._verbose:
            print("Time in "+str(self._category)+": "+str(calculated_time))
            self._verbose = False
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


def start_profiling():
    pr = cProfile.Profile()
    pr.enable()
    return pr


def stop_profiling(pr):
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


def findall_regular_expression(re_pattern, str):
    p = re.compile(re_pattern)  # res will only include patterns matched inside ()
    res = p.findall(str)
    return res

def search_regular_expression(re_pattern, str):
    p = re.compile(re_pattern)  # res will only include patterns matched inside ()
    res = p.search(str)
    return res

def match_regular_expression(re_pattern, str):
    p = re.compile(re_pattern)  # res will only include patterns matched inside ()
    res = p.match(str)
    return res

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
            if r not in visited:
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

def get_vars_as_keys(f, rs=[]):
    return [v.get_id() for v in get_vars(f,rs)]

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
            return vset(rs + [f],get_id)

    else:
        for f_ in f.children():
            rs = get_vars(f_,rs)

        return vset(rs,get_id)

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

##############################################################

# Taken from https://www.python-course.eu/graphs_python.php

""" A Python Class
A simple Python graph class, demonstrating the essential 
facts and functionalities of graphs.
"""


class MyGraph(object):

    def __init__(self, graph_dict=None):
        """ initializes a graph object
            If no dictionary or None is given,
            an empty dictionary will be used
        """
        if graph_dict == None:
            graph_dict = {}
        self.__graph_dict = graph_dict

    def vertices(self):
        """ returns the vertices of a graph """
        return list(self.__graph_dict.keys())

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in
            self.__graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary.
            Otherwise nothing has to be done.
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple or list;
            between two vertices can be multiple edges!
        """
        edge = set(edge)
        (vertex1, vertex2) = tuple(edge)
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
        else:
            self.__graph_dict[vertex1] = [vertex2]

    def __generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.__graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res

    def find_path(self, start_vertex, end_vertex, path=None):
        """ find a path from start_vertex to end_vertex
            in graph """
        if path == None:
            path = []
        graph = self.__graph_dict
        path = path + [start_vertex]
        if start_vertex == end_vertex:
            return path
        if start_vertex not in graph:
            return None
        for vertex in graph[start_vertex]:
            if vertex not in path:
                extended_path = self.find_path(vertex,
                                               end_vertex,
                                               path)
                if extended_path:
                    return extended_path
        return None