from tester import *

from PIL import Image

def test_pil184():
    # Check reading of files where xmin/xmax is not zero.

    file = "Tests/images/pil184.pcx"
    im = Image.open(file)

    assert_equal(im.size, (447, 144))
    assert_equal(im.tile[0][1], (0, 0, 447, 144))

    # Make sure all pixels are either 0 or 255.
    assert_equal(im.histogram()[0] + im.histogram()[255], 447*144)
