#
# The Python Imaging Library.
# $Id$
#
# OpenEXR file handler (work in progress)
#
# history:
# 2009-03-16 fl   Created (identify only)
#
# Copyright (c) 2009 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import struct
import Image, ImageFile

# Image.DEBUG = 2

class AttributeStream:
    def __init__(self, fp):
        self.fp = fp
        self.buf = ""
    def readstr(self):
        while "\0" not in self.buf:
            s = self.fp.read(512)
            if not s:
                raise SyntaxError("unexpected end of file")
            self.buf = self.buf + s
        value, self.buf = self.buf.split("\0", 1)
        return value
    def read(self, size):
        if len(self.buf) < size:
            s = self.fp.read(size - len(self.buf))
            if not s:
                raise SyntaxError("unexpected end of file")
            self.buf = self.buf + s
        value, self.buf = self.buf[:size], self.buf[size:]
        return value

def chlist(x):
    channels = []
    while x:
        name, x = x.split("\0", 1)
        if not name:
            break
        type, linear, x_sampling, y_sampling = struct.unpack("<4i", x[:16])
        x = x[16:]
        channels.append((name, type, linear, (x_sampling, y_sampling)))
    return channels

class preview:
    def __init__(self, x):
        self.mode = "RGBA"
        self.size = struct.unpack("<4I", x[:8])
        self.data = x[8:]
    def __repr__(self):
        return "<preview %s %s at %x>" % (self.mode, self.size, id(self))

converters = dict(
    box2f=lambda x: struct.unpack("<4f", x),
    box2i=lambda x: struct.unpack("<4i", x),
    chlist=chlist,
    chromacities=lambda x: struct.unpack("<8f", x),
    compression=ord,
    double=lambda x: struct.unpack("<d", x)[0],
    envmap=ord,
    float=lambda x: struct.unpack("<f", x)[0],
    keycode=lambda x: struct.unpack("<7i", x),
    lineOrder=ord,
    preview=preview,
    rational=lambda x: struct.unpack("<iI", x),
    string=lambda x: x[4:],
    timecode=lambda x: struct.unpack("<II", x),
    v2f=lambda x: struct.unpack("<2f", x),
    v2i=lambda x: struct.unpack("<2i", x),
    v3f=lambda x: struct.unpack("<3f", x),
    v3i=lambda x: struct.unpack("<3i", x),
    )

modes = {
    ("BY", "RY", "Y"): "YBR",
    ("B", "G", "R"): "RGB",
    ("A", "B", "G", "R"): "RGBA",
    }

# --------------------------------------------------------------------

def _accept(prefix):
    return prefix[:5] == "\x76\x2f\x31\x01\x02"

class OpenExrImageFile(ImageFile.ImageFile):

    format = "EXR"
    format_description = "OpenEXR"

    def _open(self):

        head = self.fp.read(8)
        if not _accept(head):
            raise SyntaxError("Not an OpenEXR file")

        # read attributes
        stream = AttributeStream(self.fp)
        attributes = []
        while 1:
            key = stream.readstr()
            if not key:
                break
            type = stream.readstr()
            size = struct.unpack("<I", stream.read(4))[0] 
            value = stream.read(size)
            try:
                value = converters[type](value)
            except:
                import traceback
                value = type, value
            attributes.append((key, value))

        self.info = dict(attributes)

        bbox = self.info["displayWindow"]

        channels = [channel[0] for channel in self.info["channels"]]
        channels.sort()

        self.mode = modes[tuple(channels)]
        self.size = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # print self.mode, self.size
        # print self.info

# --------------------------------------------------------------------

Image.register_open(OpenExrImageFile.format, OpenExrImageFile, _accept)

Image.register_extension(OpenExrImageFile.format, ".exr")
