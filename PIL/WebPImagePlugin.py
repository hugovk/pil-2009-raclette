#
# The Python Imaging Library.
# $Id$
#
# (Limited) WebP support for PIL
#
# History:
# 2011-06-26 fl     Created
#
# Copyright (c) Fredrik Lundh 2011.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.1"

import Image
import ImageFile

def _accept(prefix):
    return prefix[:4] == "RIFF" and prefix[8:16] == "WEBPVP8 "

##
# Image plugin for WebP images.

class WebPImageFile(ImageFile.ImageFile):

    format = "WEBP"
    format_description = "WebP image"

    def _open(self):

        container_header = self.fp.read(20)
        if not _accept(container_header):
            raise SyntaxError("not a WebP file")

        frame_header = self.fp.read(10)
        if frame_header[3:6] != "\x9d\x01\x2a":
            raise SyntaxError("unsupported WebP frame signature")

        data = map(ord, frame_header)

        # read frame tag
        tag = data[0] | (data[1] << 8) | (data[2] << 16)

        frame_type = (tag & 1) # 0=key frame, 1=interframe
        version = (((tag >> 1) & 7) > 3)
        show_frame = ((tag >> 4) & 1)
        partition_size = (tag >> 5)

        if frame_type != 0 or not show_frame:
            raise SyntaxError("not a visible WebP frame")

        xsize = ((data[7] << 8) | data[6]) & 0x3fff
        ysize = ((data[9] << 8) | data[8]) & 0x3fff

        self.mode = "RGB" # file is always YCbCr (w. chroma subsampling)
        self.size = xsize, ysize
        self.tile = [("webp", (0, 0) + self.size, 0, (self.mode, 0, 1))]

#
# --------------------------------------------------------------------

Image.register_open("WEBP", WebPImageFile, _accept)
# Image.register_save("WEBP", _save)

Image.register_extension("WEBP", ".webp")
