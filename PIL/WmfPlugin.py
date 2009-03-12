#
# The Python Imaging Library
# $Id: WmfPlugin.py 319 2004-02-23 08:39:34Z fredrik $
#
# WMF renderer
#
# history:
# 2004-02-22 fl   Created (windows support only)
#
# Copyright (c) 2004 by Fredrik Lundh.  All rights reserved.
#
# See the README file for information on usage and redistribution.
#

import Image
import WmfImagePlugin

try:
    import _pilwmf
except ImportError:
    raise ImportError("WMF support is not available for this platform")

class WmfHandler:

    def open(self, im):
        im.mode = "RGB"
        self.bbox = im.info["wmf_bbox"]

    def load(self, im):
        im.fp.seek(0) # rewind
        return Image.fromstring(
            "RGB", im.size, _pilwmf.load(im.fp.read(), im.size, self.bbox),
            "raw", "BGR", (im.size[0]*3 + 3) & -4, -1
            )

WmfImagePlugin.register_handler(WmfHandler())
