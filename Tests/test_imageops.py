from tester import *

from PIL import Image
from PIL import ImageOps

im_rgb = Image.open("Images/lena.ppm")
im = im_rgb.convert("L")

class Deformer:
    def getmesh(self, im):
        x, y = im.size
        return [((0, 0, x, y), (0, 0, x, 0, x, y, y, 0))]

deformer = Deformer()

def test_sanity():

    ImageOps.autocontrast(im)
    ImageOps.autocontrast(im_rgb)

    ImageOps.colorize(im, (0, 0, 0), (255, 255, 255))
    ImageOps.colorize(im, "black", "white")

    ImageOps.crop(im, 1)
    ImageOps.crop(im_rgb, 1)

    ImageOps.deform(im, deformer)
    ImageOps.deform(im_rgb, deformer)

    ImageOps.equalize(im)
    ImageOps.equalize(im_rgb)

    ImageOps.expand(im, 1)
    ImageOps.expand(im_rgb, 1)
    ImageOps.expand(im, 2, "blue")
    ImageOps.expand(im_rgb, 2, "blue")

    ImageOps.fit(im, (128, 128))
    ImageOps.fit(im_rgb, (128, 128))

    ImageOps.flip(im)
    ImageOps.flip(im_rgb)

    ImageOps.grayscale(im)
    ImageOps.grayscale(im_rgb)

    ImageOps.invert(im)
    ImageOps.invert(im_rgb)

    ImageOps.mirror(im)
    ImageOps.mirror(im_rgb)

    ImageOps.posterize(im, 4)
    ImageOps.posterize(im_rgb, 4)

    ImageOps.solarize(im)
    ImageOps.solarize(im_rgb)

    success()

def test_pil163():
    # Division by zero in equalize if < 255 pixels in image (@PIL163)

    i = im_rgb.resize((15, 16))

    ImageOps.equalize(i.convert("L"))
    ImageOps.equalize(i.convert("P"))
    ImageOps.equalize(i.convert("RGB"))

    success()
