from tester import *

from PIL import Image

# --------------------------------------------------------------------

def test_archive():
    import glob
    for file in glob.glob("../pil-archive/*.tif"):
        try:
            im = Image.open(file)
            im.load()
        except:
            print "- failed to open", file
        else:
            success()

# --------------------------------------------------------------------

def test_mac_tiff():
    # Read RGBa images from Mac OS X [@PIL136]

    file = "Tests/images/pil136.tiff"
    im = Image.open(file)

    assert_equal(im.mode, "RGBA")
    assert_equal(im.size, (55, 43))
    assert_equal(im.tile, [('raw', (0, 0, 55, 43), 8, ('RGBa', 0, 1))])
    assert_no_exception(lambda: im.load())

def test_gimp_tiff():
    # Read TIFF JPEG images from GIMP [@PIL168]

    file = "Tests/images/pil168.tif"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (256, 256))
    assert_equal(im.tile, [
            ('jpeg', (0, 0, 256, 64), 8, ('RGB', '')),
            ('jpeg', (0, 64, 256, 128), 1215, ('RGB', '')),
            ('jpeg', (0, 128, 256, 192), 2550, ('RGB', '')),
            ('jpeg', (0, 192, 256, 256), 3890, ('RGB', '')),
            ])
    assert_no_exception(lambda: im.load())
