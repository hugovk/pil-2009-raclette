from tester import *

from PIL import Image

def test_split():
    def split(mode):
        layers = lena(mode).split()
        return [(i.mode, i.size[0], i.size[1]) for i in layers]
    assert_equal(split("1"), [('1', 128, 128)])
    assert_equal(split("L"), [('L', 128, 128)])
    assert_equal(split("I"), [('I', 128, 128)])
    assert_equal(split("F"), [('F', 128, 128)])
    assert_equal(split("P"), [('P', 128, 128)])
    assert_equal(split("RGB"), [('L', 128, 128), ('L', 128, 128), ('L', 128, 128)])
    assert_equal(split("RGBA"), [('L', 128, 128), ('L', 128, 128), ('L', 128, 128), ('L', 128, 128)])
    assert_equal(split("CMYK"), [('L', 128, 128), ('L', 128, 128), ('L', 128, 128), ('L', 128, 128)])
    assert_equal(split("YCbCr"), [('L', 128, 128), ('L', 128, 128), ('L', 128, 128)])

def test_split_merge():
    def split_merge(mode):
        return Image.merge(mode, lena(mode).split())
    assert_image_equal(lena("1"), split_merge("1"))
    assert_image_equal(lena("L"), split_merge("L"))
    assert_image_equal(lena("I"), split_merge("I"))
    assert_image_equal(lena("F"), split_merge("F"))
    assert_image_equal(lena("P"), split_merge("P"))
    assert_image_equal(lena("RGB"), split_merge("RGB"))
    assert_image_equal(lena("RGBA"), split_merge("RGBA"))
    assert_image_equal(lena("CMYK"), split_merge("CMYK"))
    assert_image_equal(lena("YCbCr"), split_merge("YCbCr"))
