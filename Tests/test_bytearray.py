from tester import *

from PIL import ByteArray

def test_array():

    array = ByteArray.ByteArray("\x00\x01\x02\x03")

    assert_true(array)
    assert_equal(len(array), 4)
    assert_equal(len(array+array), 8)

    # assert_exception(IndexError, lambda: array[-1]) ???
    assert_equal(array[0], 0x00)
    assert_equal(array[3], 0x03)
    assert_exception(IndexError, lambda: array[4])

    assert_equal(array.int16(0), 0x0100)
    assert_equal(array.int16(1), 0x0201)
    assert_equal(array.int16(2), 0x0302)
    assert_exception(IndexError, lambda: array.int16(3))
    assert_equal(array.int32(0), 0x03020100)
    assert_exception(IndexError, lambda: array.int32(1))

    assert_equal(array.int16b(0), 0x0001)
    assert_equal(array.int16b(1), 0x0102)
    assert_equal(array.int16b(2), 0x0203)
    assert_exception(IndexError, lambda: array.int16b(3))
    assert_equal(array.int32b(0), 0x00010203)
    assert_exception(IndexError, lambda: array.int32b(1))

    assert_equal(array[1:3].tostring(), "\x01\x02")

    assert_equal(array.find("\x03"), 3)
    assert_equal(array.find("\x04"), -1)

    assert_true(array.startswith("\x00"))
    assert_false(array.startswith("\x01"))

    assert_equal(array[:1].tostring(), "\x00")
    assert_equal(array[3:].tostring(), "\x03")

    assert_equal(array.unpack("b"), 0)
    assert_equal(array.unpack("b", 3), 3)
    assert_equal(array.unpack("bbbb"), (0, 1, 2, 3))
    assert_exception(ValueError, lambda: array.unpack("ii"))

