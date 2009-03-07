from tester import *

from PIL import Image

im = Image.open("Images/lena.ppm")

def test_resize():
    def resize(mode, size):
        out = im.convert(mode).resize(size)
        assert_equal(out.mode, mode)
        assert_equal(out.size, size)
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield resize, mode, (100, 100)
        yield resize, mode, (200, 200)
