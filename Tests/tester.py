# some test helpers

_target = None
_failure = _success = 0

def success():
    global _success
    _success = _success + 1

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
    if v:
        success()
    else:
        failure(msg or "got %r, expected true value" % v)

def assert_false(v, msg=None):
    if v:
        failure(msg or "got %r, expected false value" % v)
    else:
        success()

def assert_equal(a, b, msg=None):
    if a == b:
        success()
    else:
        failure(msg or "got %r, expected %r" % (a, b))

def assert_exception(exc_class, func):
    import sys, traceback
    try:
        func()
    except exc_class:
        success()
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
    else:
        success()

# helpers

from cStringIO import StringIO

# test runner

def run():
    global _target, _failure, run
    import sys, traceback
    _target = sys.modules["__main__"]
    run = None # no need to run twice
    tests = []
    for name, value in vars(_target).items():
        if name[:5] == "test_" and type(value) is type(success):
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
                    _target.__file__, lineno, v)
                _failure = _failure + 1

def skip(msg=None):
    import os
    print "skip"
    os._exit(0) # don't run exit handlers

def _setup():
    def report():
        if run:
            run()
        if _success and not _failure:
            print "ok"
    import atexit
    atexit.register(report)

_setup()
