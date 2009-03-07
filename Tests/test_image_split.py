from tester import *

from PIL import Image

def test_split():
    def split(mode):
        layers = image_lena(mode).split()
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

def test_split_roundtrip():
    def roundtrip(mode):
        return Image.merge(mode, lena_image(mode).split())
    assert_image_equal(lena_image("1"), roundtrip("1"))
    assert_image_equal(lena_image("L"), roundtrip("L"))
    assert_image_equal(lena_image("I"), roundtrip("I"))
    assert_image_equal(lena_image("F"), roundtrip("F"))
    assert_image_equal(lena_image("P"), roundtrip("P"))
    assert_image_equal(lena_image("RGB"), roundtrip("RGB"))
    assert_image_equal(lena_image("RGBA"), roundtrip("RGBA"))
    assert_image_equal(lena_image("CMYK"), roundtrip("CMYK"))
    assert_image_equal(lena_image("YCbCr"), roundtrip("YCbCr"))
