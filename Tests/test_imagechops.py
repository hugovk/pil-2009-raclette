from tester import *

from PIL import Image
from PIL import ImageChops

def test_sanity():
    pass # FIXME

def test_logical():

    def table(op, a, b):
        out = []
        for x in (a, b):
            imx = Image.new("1", (1, 1), x)
            for y in (a, b):
                imy = Image.new("1", (1, 1), y)
                out.append(op(imx, imy).getpixel((0, 0)))
        return tuple(out)

    assert_equal(table(ImageChops.logical_and, 0, 1), (0, 0, 0, 255))
    assert_equal(table(ImageChops.logical_or, 0, 1), (0, 255, 255, 255))
    assert_equal(table(ImageChops.logical_xor, 0, 1), (0, 255, 255, 0))

    assert_equal(table(ImageChops.logical_and, 0, 128), (0, 0, 0, 255))
    assert_equal(table(ImageChops.logical_or, 0, 128), (0, 255, 255, 255))
    assert_equal(table(ImageChops.logical_xor, 0, 128), (0, 255, 255, 0))

    assert_equal(table(ImageChops.logical_and, 0, 255), (0, 0, 0, 255))
    assert_equal(table(ImageChops.logical_or, 0, 255), (0, 255, 255, 255))
    assert_equal(table(ImageChops.logical_xor, 0, 255), (0, 255, 255, 0))
