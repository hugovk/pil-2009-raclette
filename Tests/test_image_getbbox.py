from tester import *

from PIL import Image

def test_sanity():

    bbox = lena().getbbox()
    assert_true(isinstance(bbox, tuple))

    bbox = Image.new("RGB", (100, 100), 0).getbbox()
    assert_true(bbox is None)

