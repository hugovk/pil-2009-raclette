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
    bytes = out.tell()
    out.seek(0)
    im = Image.open(out)
    im.bytes = bytes # for testing only
    return im

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
    # Test CMYK handling.  Thanks to Tim and Charlie for test data,
    # Michael for getting me to look one more time.
    file = "Tests/images/pil_sample_cmyk.jpg"
    im = Image.open(file)
    # the source image has red pixels in the upper left corner.
    c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
    assert_true(c == 0.0 and m > 0.8 and y > 0.8 and k == 0.0)
    # the opposite corner is black
    c, m, y, k = [x / 255.0 for x in im.getpixel((im.size[0]-1, im.size[1]-1))]
    assert_true(k > 0.9)
    # roundtrip, and check again
    im = roundtrip(im)
    c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
    assert_true(c == 0.0 and m > 0.8 and y > 0.8 and k == 0.0)
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

def test_icc():
    # Test ICC support
    im1 = Image.open("Tests/images/rgb.jpg")
    icc_profile = im1.info["icc_profile"]
    assert_equal(len(icc_profile), 3144)
    # In 1.1.7a2, ICC write only works if im.info contains a icc_profile
    # key and output is written to a file
    file = tempfile("temp.jpg")
    im1.save(file)
    im2 = Image.open(file)
    assert_equal(im1.info["icc_profile"], icc_profile)
    # Do roundtrip testing.  The last one will fail in 1.1.7a2.
    im2 = roundtrip(im1)
    im3 = roundtrip(im1, icc_profile=icc_profile)
    assert_image_equal(im2, im3)
    assert_true(im1.info.get("icc_profile"))
    assert_false(im2.info.get("icc_profile"))
    assert_true(im3.info.get("icc_profile")) # bug in 1.1.7a2

def test_optimize():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), optimize=1)
    assert_image_equal(im1, im2)
    assert_true(im1.bytes >= im2.bytes)

def test_progressive():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), progressive=1)
    im3 = roundtrip(lena(), progression=1) # compatibility
    assert_image_equal(im1, im2)
    assert_image_equal(im1, im3)
    assert_false(im1.info.get("progressive"))
    assert_false(im1.info.get("progression"))
    assert_true(im2.info.get("progressive"))
    assert_true(im2.info.get("progression"))
    assert_true(im3.info.get("progressive"))
    assert_true(im3.info.get("progression"))

def test_quality():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), quality=50)
    assert_image(im1, im2.mode, im2.size)
    assert_true(im1.bytes >= im2.bytes)

def test_smooth():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), smooth=100)
    assert_image(im1, im2.mode, im2.size)

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
