from tester import *

from PIL import Image

im = Image.open("Images/lena.ppm")

def test_putpalette():
    def palette(mode):
        i = im.convert(mode)
        i.putpalette(range(256)*3)
        p = i.getpalette()
        if p:
            return i.mode, p[:10]
        return i.mode
    assert_exception(ValueError, lambda: palette("1"))
    assert_equal(palette("L"), ("P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    assert_equal(palette("P"), ("P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    assert_exception(ValueError, lambda: palette("I"))
    assert_exception(ValueError, lambda: palette("F"))
    assert_exception(ValueError, lambda: palette("RGB"))
    assert_exception(ValueError, lambda: palette("RGBA"))
    assert_exception(ValueError, lambda: palette("YCbCr"))
