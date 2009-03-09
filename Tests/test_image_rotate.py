from tester import *

from PIL import Image

def test_rotate():
    def rotate(mode):
        im = lena(mode)
        out = im.rotate(45)
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size) # default rotate clips output
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield_test(rotate, mode)
