# PILusm.py
# by Kevin Cazabon (kevin@cazabon.com, kevin_cazabon@hotmail.com)
# copyright 2003

#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

try:
    from PIL import Image
except ImportError:
    import Image
    
import PILusm

def gblur(im, radius = None):
    """ PIL_usm.gblur(im, [radius])"""
    
    if radius == None:
        radius = 5.0

    if not im.mode in ["RGB", "RGBX", "RGBA", "CMYK", "L"]:
        raise TypeError, "Only RGB, RGBX, RGBA, CMYK, and L mode images supported."

    im.load()
    imOut = Image.new(im.mode, im.size)

    result = PILusm.gblur(im.im.id, imOut.im.id, float(radius))
    
    if result[0] != 0:
        raise Exception, result[1]

    return imOut

def usm(im, radius = None, percent = None, threshold = None):
    """ PIL_usm.usm(im, [radius, percent, threshold])"""
    
    if radius == None:
        radius = 5.0
    if percent == None:
        percent = 150
    if threshold == None:
        threshold = 3

    if not im.mode in ["RGB", "RGBX", "RGBA", "CMYK", "L"]:
        raise TypeError, "Only RGB, RGBX, RGBA, CMYK, and L mode images supported."

    im.load()
    imOut = Image.new(im.mode, im.size)

    result = PILusm.usm(im.im.id, imOut.im.id, float(radius), int(percent), int(threshold))    

    if result[0] != 0:
        raise Exception, result[1]

    return imOut


if __name__ == "__main__":
    im = Image.open("c:\\temp\\test.tif")

    import time

    start = time.time()

    im1 = gblur(im, 2.0)
    print "gblur done in %s seconds" %(time.time() - start)
    im1.save("c:\\temp\\test_blur.tif")

    start = time.time()
    im2 = usm(im, 2.0, 125, 8)
    print "usm done in %s seconds" %(time.time() - start)
    im2.save("c:\\temp\\test_usm.tif")

    #start = time.time()
    #im2 = antiNoise(im, 6, 6)
    #print "antiNoise done in %s seconds" %(time.time() - start)
    #im2.save("c:\\temp\\test_antiNoise_c.png")






