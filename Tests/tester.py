# some test helpers

_target = None
_failure = 0

def failure(msg=None, frame=None):
    global _failure
    import sys, linecache
    _failure = _failure + 1
    if _target:
        if frame is None:
            frame = sys._getframe()
            while frame.f_globals.get("__name__") != _target.__name__:
                frame = frame.f_back
        location = (frame.f_code.co_filename, frame.f_lineno)
        prefix = "%s:%d: " % location
        line = linecache.getline(*location)
        print prefix + line.strip() + " failed:"
    if msg:
        print "- " + msg

# predicates

def assert_true(v, msg=None):
    if not v: failure(msg or "got %r, expected true value" % v)

def assert_false(v, msg=None):
    if v: failure(msg or "got %r, expected false value" % v)

def assert_equal(a, b, msg=None):
    if a != b: failure(msg or "got %r, expected %r" % (a, b))

def assert_exception(exc_class, func):
    import sys, traceback
    try:
        func()
    except exc_class:
        pass
    except:
        failure("expected %r exception, got %r" % (
                exc_class.__name__, sys.exc_type.__name__))
        traceback.print_exc()
    else:
        failure("expected %r exception, got no exception" % exc_class.__name__)

def assert_no_exception(func):
    import sys, traceback
    try:
        func()
    except:
        failure("expected no exception, got %r" % sys.exc_type.__name__)
        traceback.print_exc()

# helpers

from cStringIO import StringIO

# test runner

def run():
    global _target, _failure
    import sys, traceback
    namespace = sys._getframe().f_back.f_globals # FIXME: iterate to find top
    _target = sys.modules[namespace["__name__"]]
    tests = []
    for name, value in namespace.items():
        if name[:5] == "test_" and type(value) is type(run):
            tests.append((value.func_code.co_firstlineno, name, value))
    tests.sort() # sort by line
    for lineno, name, func in tests:
        try:
            func()
        except:
            t, v, tb = sys.exc_info()
            tb = tb.tb_next
            if tb:
                failure(frame=tb.tb_frame)
                traceback.print_exception(t, v, tb)
            else:
                print "%s:%d: cannot call test function: %s" % (
                    namespace["__file__"], lineno, v)
                _failure = _failure + 1

def skip(msg=None):
    import os
    print "skip"
    os._exit(0) # don't run exit handlers

def _setup():
    def report():
        if not _failure:
            print "ok"
    import atexit
    atexit.register(report)

_setup()
