from tester import *

from PIL import Image

codecs = dir(Image.core)

if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
    skip("jpeg support not available")

# sample jpeg stream
file = "Images/lena.jpg"
data = open(file, "rb").read()

def roundtrip(im, **options):
    out = StringIO()
    im.save(out, "JPEG", **options)
    out.seek(0)
    return Image.open(out)

# --------------------------------------------------------------------

def test_sanity():

    # internal version number
    assert_match(Image.core.jpeglib_version, "\d+\.\d+$")

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "JPEG")

# --------------------------------------------------------------------

def test_app():
    # Test APP/COM reader (@PIL135)
    im = Image.open(file)
    assert_equal(im.applist[0],
                 ("APP0", "JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"))
    assert_equal(im.applist[1], ("COM", "Python Imaging Library"))
    assert_equal(len(im.applist), 2)

def test_cmyk():
    # Test CMYK handling.  Thanks to Tim and Charlie for test data.
    file = "Tests/images/pil_sample_cmyk.jpg"
    im = Image.open(file)
    # the source image has red pixels in the upper left corner.  with
    # the default color profile, that gives us medium cyan/magenta and
    # plenty of yellow.  don't ask.
    c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
    assert_true(c < 0.4 and m < 0.4 and y > 0.9 and k == 0.0)
    # the opposite corner is black
    c, m, y, k = [x / 255.0 for x in im.getpixel((im.size[0]-1, im.size[1]-1))]
    assert_true(k > 0.9)
    # roundtrip, and check again
    im = roundtrip(im)
    c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
    assert_true(c > 0.3 and m > 0.3 and y > 0.9 and k == 0.0)
    c, m, y, k = [x / 255.0 for x in im.getpixel((im.size[0]-1, im.size[1]-1))]
    assert_true(k > 0.9)

def test_dpi():
    def test(xdpi, ydpi=None):
        im = Image.open(file)
        im = roundtrip(im, dpi=(xdpi, ydpi or xdpi))
        return im.info.get("dpi")
    assert_equal(test(72), (72, 72))
    assert_equal(test(300), (300, 300))
    assert_equal(test(100, 200), (100, 200))
    assert_equal(test(0), None) # square pixels

def test_subsampling():
    def getsampling(im):
        layer = im.layer
        return layer[0][1:3] + layer[1][1:3] + layer[2][1:3]
    # experimental API
    im = roundtrip(lena(), subsampling=-1) # default
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=0) # 4:4:4
    assert_equal(getsampling(im), (1, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=1) # 4:2:2
    assert_equal(getsampling(im), (2, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=2) # 4:1:1
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=3) # default (undefined)
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))

    im = roundtrip(lena(), subsampling="4:4:4")
    assert_equal(getsampling(im), (1, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling="4:2:2")
    assert_equal(getsampling(im), (2, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling="4:1:1")
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))

    assert_exception(TypeError, lambda: roundtrip(lena(), subsampling="1:1:1"))

def test_truncated_jpeg():
    def test(junk):
        if junk:
            # replace "junk" bytes at the end with junk
            file = StringIO(data[:-junk] + (junk*chr(0)))
        else:
            file = StringIO(data)
        im = Image.open(file)
        im.load()
    assert_no_exception(lambda: test(0))
    assert_exception(IOError, lambda: test(1))
    assert_no_exception(lambda: test(2))
    assert_no_exception(lambda: test(4))
    assert_no_exception(lambda: test(8))
    assert_exception(IOError, lambda: test(10))
