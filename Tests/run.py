# minimal test runner

import os, sys

root = os.path.dirname(__file__)

tests = []
failed = []

for file in os.listdir(root):
    if file[:5] == "test_" and file[-3:] == ".py":
        if file == "test_sanity.py":
            tests.insert(0, file)
        else:
            tests.append(file)

for test in tests:
    print test, "..."
    file = os.path.join(root, test)
    out = os.popen(sys.executable + " -u " + file + " 2>&1")
    result = out.read()
    if result.strip() == "ok":
        result = None
    status = out.close()
    if status or result:
        if status:
            print "- error", status
        if result:
            print result
        failed.append(test)

if failed:
    print "*** %s tests of %d failed." % (len(failed), len(tests))
else:
    print "%s tests passed." % len(tests)
