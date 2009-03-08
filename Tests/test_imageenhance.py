from tester import *

from PIL import Image
from PIL import ImageEnhance

def test_sanity():
    
    # FIXME: assert_image
    assert_no_exception(lambda: ImageEnhance.Color(lena()).enhance(0.5))
    assert_no_exception(lambda: ImageEnhance.Contrast(lena()).enhance(0.5))
    assert_no_exception(lambda: ImageEnhance.Brightness(lena()).enhance(0.5))
    assert_no_exception(lambda: ImageEnhance.Sharpness(lena()).enhance(0.5))
