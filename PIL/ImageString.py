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

def join(seq, sep):
    return sep.join(seq)

def split(s, sep=None, maxsplit=None):
    if sep is None:
        return s.split()
    if maxsplit is None:
        return s.split(sep)
    return s.split(sep, maxsplit)
