from PIL import Image
from PIL import ImageStat

im = Image.new("L", (100, 100))

stat = ImageStat.Stat(im)

print "ok"
