# PILusm.py
# by Kevin Cazabon (kevin@cazabon.com, kevin_cazabon@hotmail.com)
# copyright 2003

from PIL import Image, ImageOps

if 1:

    im = Image.open("Images/lena.ppm")

    import time

    start = time.time()

    im1 = ImageOps.gblur(im, 2.0)
    print "gblur done in %s seconds" %(time.time() - start)
    im1.save("blur.bmp")

    start = time.time()
    im2 = ImageOps.usm(im, 2.0, 125, 8)
    print "usm done in %s seconds" %(time.time() - start)
    im2.save("usm.bmp")





