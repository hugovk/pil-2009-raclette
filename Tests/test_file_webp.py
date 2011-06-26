from tester import *

from PIL import Image
from PIL import WebPImagePlugin

codecs = dir(Image.core)

# if "webp_decoder" not in codecs:
#     skip("webp support not available")

def test_sanity():

    # internal version number
    # assert_match(Image.core.webp_version, "\d+\.\d+\.\d+(\.\d+)?$")

    im = Image.open("Images/lena.webp")
    # im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "WEBP")
