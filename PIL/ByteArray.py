#
# The Python Imaging Library.
# $Id$
#
# simple <byte array type
#
# history:
# 2011-01-05 fl   Created
#
# Copyright (c) 2011 by Secret Labs AB
# Copyright (c) 2011 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import struct

class ByteArray(object):

    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __add__(self, other):
        return ByteArray(self.data + other.data)

    def __getitem__(self, i):
        return ord(self.data[i])

    def find(self, p):
        return self.data.find(p)

    def int16(self, i):
        return self[i] + (self[i+1]<<8)

    def int32(self, i):
        return self[i] + (self[i+1]<<8) + (self[i+2]<<16) + (self[i+3]<<24)

    def int16b(self, i):
        return self[i+1] + (self[i]<<8)

    def int32b(self, i):
        return self[i+3] + (self[i+2]<<8) + (self[i+1]<<16) + (self[i]<<24)

    def __getslice__(self, i, j):
        return ByteArray(self.data[i:j])

    def startswith(self, s):
        return self.data[:len(s)] == s

    def tostring(self):
        return self.data

    def unpack(self, fmt, i=0):
        try:
            n = struct.calcsize(fmt)
            v = struct.unpack(fmt, self.data[i:i+n])
        except struct.error, v:
            raise ValueError(v)
        if len(v) == 1:
            v = v[0] # singleton
        return v
