from tester import *

from PIL import Image
from PIL import ImageOps

im = Image.open("Images/lena.ppm")

def test_sanity():

    i = ImageOps.gaussian_blur(im, 2.0)
    assert_equal(i.mode, "RGB")
    assert_equal(i.size, (128, 128))
    # i.save("blur.bmp")

    i = ImageOps.usm(im, 2.0, 125, 8)
    assert_equal(i.mode, "RGB")
    assert_equal(i.size, (128, 128))
    # i.save("usm.bmp")



