#
# The Python Imaging Library.
# $Id: IcoImagePlugin.py 2134 2004-10-06 08:55:20Z fredrik $
#
# Windows Icon support for PIL
#
# Notes:
#       uses BmpImagePlugin.py to read the bitmap data.
#
# History:
#       96-05-27 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.2"

import Image
import BmpImagePlugin, PngImagePlugin

from cStringIO import StringIO

#
# --------------------------------------------------------------------

def i8(c):
    return ord(c) or 256

def i16(c):
    return ord(c[0]) + (ord(c[1])<<8)

def i32(c):
    return ord(c[0]) + (ord(c[1])<<8) + (ord(c[2])<<16) + (ord(c[3])<<24)


def _accept(prefix):
    return prefix[:4] == "\0\0\1\0"

##
# Image plugin for Windows Icon files.

class IcoImageFile(BmpImagePlugin.BmpImageFile):

    format = "ICO"
    format_description = "Windows Icon"

    def _open(self):

        # check magic
        s = self.fp.read(6)
        if not _accept(s):
            raise SyntaxError("not an ICO file")

        # locate icons
        self.icons = []
        index = None
        for i in range(i16(s[4:])):
            s = self.fp.read(16)
            size = i8(s[0]), i8(s[1])
            bits = i16(s[6:8])
            offset = i32(s[12:16])
            bytes = i32(s[8:12])
            self.icons.append((size, bits, offset, bytes))

        # pick biggest image
        size, bits, offset, bytes = max(self.icons)

        self.fp.seek(offset)
        data = self.fp.read(16)
        self.fp.seek(offset)

        if PngImagePlugin._accept(data):
            # FIXME: delay loading (via load hook?).  note that the
            # PNG loader uses a custom loader API, so we cannot just
            # copy the tile descriptor
            # FIXME: move custom read hooks into tile descriptor?
            im = PngImagePlugin.PngImageFile(self.fp)
            im.load() #
            self.im = im.im
            self.mode = im.mode
            self.size = im.size
            self.tile = []
        else:
            self._bitmap(offset)
            self.size = size
            d, e, o, a = self.tile[0]
            self.tile = [(d, (0,0)+size, o, a)]
            # FIXME: fetch mask

#
# --------------------------------------------------------------------

Image.register_open("ICO", IcoImageFile, _accept)

Image.register_extension("ICO", ".ico")
