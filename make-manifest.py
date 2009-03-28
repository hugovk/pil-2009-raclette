# $Id$
# generate manifest file

import string

out = open("MANIFEST", "w")

for line in open("CONTENTS").readlines():
    line = string.strip(line)
    if line:
        line = string.split(line, "Imaging/", 1)
        print >>out, line[1]
