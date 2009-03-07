from tester import *

from PIL import Image
from PIL import ImageMath

def pixel(im):
    if hasattr(im, "im"):
        return "%s %r" % (im.mode, im.getpixel((0, 0)))
    else:
        if isinstance(im, type(0)):
            return int(im) # hack to deal with booleans
        print im

A = Image.new("L", (1, 1), 1)
B = Image.new("L", (1, 1), 2)

images = {"A": A, "B": B}

def test_sanity():
    assert_equal(ImageMath.eval("1"), 1)
    assert_equal(ImageMath.eval("1+A", A=2), 3)
    assert_equal(pixel(ImageMath.eval("A+B", A=A, B=B)), "I 3")
    assert_equal(pixel(ImageMath.eval("A+B", images)), "I 3")
    assert_equal(pixel(ImageMath.eval("float(A)+B", images)), "F 3.0")
    assert_equal(pixel(ImageMath.eval("int(float(A)+B)", images)), "I 3")

def test_logical():
    assert_equal(pixel(ImageMath.eval("not A", images)), 0)
    assert_equal(pixel(ImageMath.eval("A and B", images)), "L 2")
    assert_equal(pixel(ImageMath.eval("A or B", images)), "L 1")

def test_convert():
    assert_equal(pixel(ImageMath.eval("convert(A+B, 'L')", images)), "L 3")
    assert_equal(pixel(ImageMath.eval("convert(A+B, '1')", images)), "1 0")
    assert_equal(pixel(ImageMath.eval("convert(A+B, 'RGB')", images)), "RGB (3, 3, 3)")

def test_compare():
    assert_equal(pixel(ImageMath.eval("min(A, B)", images)), "I 1")
    assert_equal(pixel(ImageMath.eval("max(A, B)", images)), "I 2")
    assert_equal(pixel(ImageMath.eval("A == 1", images)), "I 1")
    assert_equal(pixel(ImageMath.eval("A == 2", images)), "I 0")
