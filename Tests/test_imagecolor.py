from PIL import Image
from PIL import ImageColor

# --------------------------------------------------------------------
# sanity

assert ImageColor.getrgb("#f00") == (255, 0, 0)
assert ImageColor.getrgb("#ff0000") == (255, 0, 0)
assert ImageColor.getrgb("rgb(255,0,0)") == (255, 0, 0)
assert ImageColor.getrgb("rgb(100%,0%,0%)") == (255, 0, 0)
assert ImageColor.getrgb("hsl(0, 100%, 50%)") == (255, 0, 0)
assert ImageColor.getrgb("red") == (255, 0, 0)

# --------------------------------------------------------------------
# look for rounding errors (based on code by Tim Hatch)

def verify_color(color):
    expected = Image.new("RGB", (1, 1), color).convert("L").getpixel((0, 0))
    actual = Image.new("L", (1, 1), color).getpixel((0, 0))
    assert expected == actual, "%r: %r != %r" % (color, expected, actual)

for name in ImageColor.colormap:
    verify_color(name)

assert ImageColor.getcolor("black", "RGB") == (0, 0, 0)
assert ImageColor.getcolor("white", "RGB") == (255, 255, 255)

assert ImageColor.getcolor("black", "L") == 0
assert ImageColor.getcolor("white", "L") == 255

assert ImageColor.getcolor("black", "1") == 0
assert ImageColor.getcolor("white", "1") == 255

print "ok"
