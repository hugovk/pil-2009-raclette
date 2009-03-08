from tester import *

from PIL import Image

def test_sanity():

    def convert(im, mode):
        out = im.convert(mode)
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size)

    modes = "1", "L", "I", "F", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr"

    for mode in modes:
        im = lena(mode)
        for mode in modes:
            test(convert, im, mode)
