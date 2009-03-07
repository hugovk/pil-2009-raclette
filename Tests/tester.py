# some test helpers

_target = None
_tempfiles = []

def success():
    success.count += 1

def failure(msg=None, frame=None):
    import sys, linecache
    failure.count += 1
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

success.count = failure.count = 0

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

def fromstring(data):
    from PIL import Image
    return Image.open(StringIO(data))

def tostring(im, format, **options):
    out = StringIO()
    im.save(out, format, **options)
    return out.getvalue()

def lena(mode="RGB", cache={}):
    from PIL import Image
    im = cache.get(mode)
    if im is None:
        if mode == "RGB":
            im = Image.open("Images/lena.ppm")
        elif mode == "F":
            im = lena("L").convert(mode)
        else:
            im = lena("RGB").convert(mode)
    cache[mode] = im
    return im

def assert_image_equal(a, b, msg=None):
    if a.mode != b.mode:
        failure(msg or "got mode %r, expected %r" % (a.mode, b.mode))
    elif a.size != b.size:
        failure(msg or "got size %r, expected %r" % (a.size, b.size))
    elif a.tostring() != b.tostring():
        failure(msg or "got different content")
        # generate better diff?
    else:
        success()

def tempfile(template, *extra):
    import os, sys
    files = []
    for temp in (template,) + extra:
        assert temp[:5] in ("temp.", "temp_")
        root, name = os.path.split(sys.argv[0])
        name = temp[:4] + os.path.splitext(name)[0][4:]
        name = name + "_%d" % len(_tempfiles) + temp[4:]
        name = os.path.join(root, name)
        files.append(name)
    _tempfiles.extend(files)
    return files[0]

# test runner

def run():
    global _target, run
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
            result = func()
            if hasattr(result, "__iter__"):
                # FIXME: make failure report include the arguments
                for test in result:
                    test[0](*test[1:])
        except:
            t, v, tb = sys.exc_info()
            tb = tb.tb_next
            if tb:
                failure(frame=tb.tb_frame)
                traceback.print_exception(t, v, tb)
            else:
                print "%s:%d: cannot call test function: %s" % (
                    sys.argv[0], lineno, v)
                failure.count += 1

def skip(msg=None):
    import os
    print "skip"
    os._exit(0) # don't run exit handlers

def _setup():
    def report():
        if run:
            run()
        if success.count and not failure.count:
            print "ok"
            # only clean out tempfiles if test passed
            import os
            for file in _tempfiles:
                try:
                    os.remove(file)
                except OSError:
                    pass # report?
    import atexit
    atexit.register(report)

_setup()
