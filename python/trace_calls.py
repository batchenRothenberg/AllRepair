import collections
# usage:
#
#   import trace_calls
#   trace_calls.trace_class(MyClass)
#


# decorator
def trace_method(mthd, classname):
    def inner(*args, **kwargs):
        argstrings = []
        argstrings.extend([str(x) for x in args[1:]])
        for x, y in kwargs.items():
            argstrings.append("%s=%s" % (str(x), str(y)))
        printargs = ', '.join(argstrings)

        if mthd.__name__ == '__init__':
            print("_x = %s(%s)" % (classname, printargs))
        else:
            print("_x.%s(%s)" % (mthd.__name__, printargs))

        # actually call the method itself
        return mthd(*args, **kwargs)
    return inner


# modify a class, decorating every method with the above decorator
def trace_class(cls):
    import inspect
    for name, attr in inspect.getmembers(cls):
        if isinstance(attr, collections.Callable):
            setattr(cls, name, trace_method(attr, cls))
