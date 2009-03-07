from tester import *

from PIL import Image

def pack():
    pass # not yet

def unpack(mode, rawmode, bytes):
    data = "".join(map(chr, range(1,bytes+1)))
    im = Image.fromstring(mode, (1, 1), data, "raw", rawmode, 0, 1)
    return im.getpixel((0, 0))

def test_pack():
    pass # not yet

def test_unpack():
    assert_equal(unpack("1", "1", 1), 0)
    assert_equal(unpack("1", "1;I", 1), 255)
    assert_equal(unpack("1", "1;R", 1), 255)
    assert_equal(unpack("1", "1;IR", 1), 0)

    assert_equal(unpack("L", "L;2", 1), 0)
    assert_equal(unpack("L", "L;4", 1), 0)
    assert_equal(unpack("L", "L", 1), 1)
    assert_equal(unpack("L", "L;I", 1), 254)
    assert_equal(unpack("L", "L;R", 1), 128)
    assert_equal(unpack("L", "L;16", 2), 2) # little endian
    assert_equal(unpack("L", "L;16B", 2), 1) # big endian

    assert_equal(unpack("LA", "LA", 2), (1, 2))
    assert_equal(unpack("LA", "LA;L", 2), (1, 2))

    assert_equal(unpack("RGB", "RGB", 3), (1, 2, 3))
    assert_equal(unpack("RGB", "RGB;L", 3), (1, 2, 3))
    assert_equal(unpack("RGB", "RGB;R", 3), (128, 64, 192))
    assert_equal(unpack("RGB", "RGB;16B", 6), (1, 3, 5)) # ?
    assert_equal(unpack("RGB", "BGR", 3), (3, 2, 1))
    assert_equal(unpack("RGB", "BGR;15", 2), (0, 131, 8))
    assert_equal(unpack("RGB", "BGR;16", 2), (0, 64, 8))
    assert_equal(unpack("RGB", "RGBX", 4), (1, 2, 3))
    assert_equal(unpack("RGB", "BGRX", 4), (3, 2, 1))
    assert_equal(unpack("RGB", "XRGB", 4), (2, 3, 4))
    assert_equal(unpack("RGB", "XBGR", 4), (4, 3, 2))

    assert_equal(unpack("CMYK", "CMYK", 4), (1, 2, 3, 4))
    assert_equal(unpack("CMYK", "CMYK;I", 4), (254, 253, 252, 251))

    assert_exception(ValueError, lambda: unpack("L", "L", 0))
    assert_exception(ValueError, lambda: unpack("RGB", "RGB", 2))
    assert_exception(ValueError, lambda: unpack("CMYK", "CMYK", 2))

run()
