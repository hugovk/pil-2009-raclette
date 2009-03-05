# minimal test runner

import glob, os, sys

root = os.path.dirname(__file__)

print "-"*68

os.environ["PYTHONPATH"] = "."

files = glob.glob(os.path.join(root, "test_*.py"))
files.sort()

success = failure = 0

for file in files:
    test = os.path.basename(file)
    print test, "..."
    out = os.popen("%s -u %s 2>&1" % (sys.executable, file))
    result = out.read()
    if result.strip() == "ok":
        result = None
    status = out.close()
    if status or result:
        if status:
            print "=== error", status
        if result:
            print result
        failure = failure + 1
    else:
        success = success + 1

print "-"*68

if failure:
    print "*** %s tests of %d failed." % (failure, success + failure)
else:
    print "%s tests passed." % success
