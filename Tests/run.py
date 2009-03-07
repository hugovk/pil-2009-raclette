# minimal test runner

import glob, os, sys

root = os.path.dirname(__file__)

print "-"*68

if "--installed" in sys.argv:
    options = ""
else:
    options = "-S"
    os.environ["PYTHONPATH"] = "."

files = glob.glob(os.path.join(root, "test_*.py"))
files.sort()

success = failure = 0
include = [x for x in sys.argv[1:] if x[:2] != "--"]
skipped = []

for file in files:
    test, ext = os.path.splitext(os.path.basename(file))
    if include and test not in include:
        continue
    print "running", test, "..."
    # 2>&1 works on unix and on modern windowses.  we might care about
    # very old Python versions, but not ancient microsoft products :-)
    out = os.popen("%s %s -u %s 2>&1" % (sys.executable, options, file))
    result = out.read().strip()
    if result == "ok":
        result = None
    elif result == "skip":
        print "---", "skipped" # FIXME: driver should include a reason
        skipped.append(test)
        continue
    elif not result:
        result = "(no output)"
    status = out.close()
    if status or result:
        if status:
            print "=== error", status
        if result:
            if result[-3:] == "\nok":
                # if there's an ok at the end, it's not really ok
                result = result[:-3]
            print result
        failure = failure + 1
    else:
        success = success + 1

print "-"*68

tempfiles = glob.glob(os.path.join(root, "temp_*"))
if tempfiles:
    print "===", "remaining temporary files"
    for file in tempfiles:
        print file
    print "-"*68

if skipped:
    print "--- %d tests skipped." % len(skipped)
    print skipped
if failure:
    print "*** %d tests of %d failed." % (failure, success + failure)
else:
    print "%d tests passed." % success
