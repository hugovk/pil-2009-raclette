from tester import *

from PIL import Image

im = Image.open("Images/lena.ppm")

def test_palette():
    def palette(mode):
        p = im.convert(mode).getpalette()
        if p:
            return p[:10]
        return None
    assert_equal(palette("1"), None)
    assert_equal(palette("L"), None)
    assert_equal(palette("I"), None)
    assert_equal(palette("F"), None)
    assert_equal(palette("P"), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    assert_equal(palette("RGB"), None)
    assert_equal(palette("RGBA"), None)
    assert_equal(palette("CMYK"), None)
    assert_equal(palette("YCbCr"), None)
