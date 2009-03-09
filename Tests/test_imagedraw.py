from tester import *

from PIL import Image
from PIL import ImageDraw

def test_sanity():

    im = lena("RGB").copy()

    draw = ImageDraw.ImageDraw(im)
    draw = ImageDraw.Draw(im)

    draw.ellipse(range(4))
    draw.line(range(10))
    draw.polygon(range(100))
    draw.rectangle(range(4))

    success()
