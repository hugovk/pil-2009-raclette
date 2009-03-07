from tester import *

from PIL import Image

im = Image.new("L", (100, 100))
assert_equal(im.mode, "L")
assert_equal(im.size, (100, 100))

im = Image.new("RGB", (100, 100))
assert_equal(im.mode, "RGB")
assert_equal(im.size, (100, 100))

im1 = Image.new("L", (100, 100), None)
im2 = Image.new("L", (100, 100), 0)
im3 = Image.new("L", (100, 100), "black")

assert_equal(im2.getcolors(), [(10000, 0)])
assert_equal(im3.getcolors(), [(10000, 0)])

assert_exception(ValueError, lambda: Image.new("X", (100, 100)))
# assert_exception(MemoryError, lambda: Image.new("L", (1000000, 1000000)))
