from tester import *

from PIL import Image, FontFile, PcfFontFile
from PIL import ImageFont, ImageDraw

filename = "Tests/fonts/helvO18.pcf"
message  = "hello, world"

def test_sanity():

    file = open(filename, "rb")
    font = PcfFontFile.PcfFontFile(file)
    assert_true(isinstance(font, FontFile.FontFile))
    assert_equal(len(filter(None, font.glyph)), 192)

    font.save("temp.pil")

def test_draw():

    font = ImageFont.load("temp.pil")
    image = Image.new("L", font.getsize(message), "white")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), message, font=font)
    # assert_signature(image, "7216c60f988dea43a46bb68321e3c1b03ec62aee")
