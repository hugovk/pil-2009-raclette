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

def test_usm():

    assert_exception(ValueError, lambda: ImageOps.usm(im.convert("1")))
    assert_no_exception(lambda: ImageOps.usm(im.convert("L")))
    assert_exception(ValueError, lambda: ImageOps.usm(im.convert("I")))
    assert_exception(ValueError, lambda: ImageOps.usm(im.convert("F")))
    assert_no_exception(lambda: ImageOps.usm(im.convert("RGB")))
    assert_no_exception(lambda: ImageOps.usm(im.convert("RGBA")))
    assert_no_exception(lambda: ImageOps.usm(im.convert("CMYK")))
    assert_exception(ValueError, lambda: ImageOps.usm(im.convert("YCbCr")))

def test_blur():

    assert_exception(ValueError, lambda: ImageOps.gblur(im.convert("1")))
    assert_no_exception(lambda: ImageOps.gblur(im.convert("L")))
    assert_exception(ValueError, lambda: ImageOps.gblur(im.convert("I")))
    assert_exception(ValueError, lambda: ImageOps.gblur(im.convert("F")))
    assert_no_exception(lambda: ImageOps.gblur(im.convert("RGB")))
    assert_no_exception(lambda: ImageOps.gblur(im.convert("RGBA")))
    assert_no_exception(lambda: ImageOps.gblur(im.convert("CMYK")))
    assert_exception(ValueError, lambda: ImageOps.gblur(im.convert("YCbCr")))
