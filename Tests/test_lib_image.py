from tester import *

from PIL import Image

def test_setmode():

    im = Image.new("RGB", (1, 1), (1, 2, 3))

    im.im.setmode("RGB")
    assert_equal(im.im.getpixel((0, 0)), (1, 2, 3))

    im.im.setmode("RGBA")
    assert_equal(im.im.getpixel((0, 0)), (1, 2, 3, 255))

    im.im.setmode("RGBX")
    assert_equal(im.im.getpixel((0, 0)), (1, 2, 3, 255))

    im.im.setmode("RGB")
    assert_equal(im.im.getpixel((0, 0)), (1, 2, 3))

    assert_exception(ValueError, lambda: im.im.setmode("L"))
    assert_exception(ValueError, lambda: im.im.setmode("RGBABCDE"))
