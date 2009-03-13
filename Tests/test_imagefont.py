from tester import *

from PIL import Image
try:
    from PIL import ImageFont
    ImageFont.core.getversion() # check if freetype is available
except ImportError:
    skip()

def test_sanity():

    assert_equal(ImageFont.core.getversion(), "2.3.9")
