#
# The Python Imaging Library.
# $Id$
#
# temporary string portability layer
#
# history:
# 2011-01-05 fl   Created
#
# Copyright (c) 2011 by Secret Labs AB
# Copyright (c) 2011 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

def find(s, p):
    return s.find(p)

def index(s, p, o=0):
    return s.index(p,o)

def join(seq, sep):
    return sep.join(seq)

def ljust(s, n):
    return s.ljust(n)

def replace(s, a, b):
    return s.replace(a, b)

def split(s, sep=None, maxsplit=None):
    if sep is None:
        return s.split()
    if maxsplit is None:
        return s.split(sep)
    return s.split(sep, maxsplit)
