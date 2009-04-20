from tester import *

from PIL import Image

def test_sanity():

    im1 = lena()
    
    data = list(im1.getdata() )

    im2 = Image.new(im1.mode, im1.size, None)
    im2.putdata(data)

    assert_image_equal(im1, im2)

