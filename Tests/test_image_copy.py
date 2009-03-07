from tester import *

from PIL import Image

im = Image.open("Images/lena.ppm")

def test_copy():
    def copy(mode):
        out = im.convert(mode).copy()
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size)
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield copy, mode
