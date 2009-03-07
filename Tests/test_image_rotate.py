from tester import *

from PIL import Image

im = Image.open("Images/lena.ppm")

def test_rotate():
    def rotate(mode):
        out = im.convert(mode).rotate(45)
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size) # default rotate clips output
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield rotate, mode
