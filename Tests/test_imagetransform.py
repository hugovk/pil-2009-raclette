from PIL import Image
from PIL import ImageTransform

im = Image.new("L", (100, 100))
seq = tuple(range(10))

im.transform((100, 100), ImageTransform.AffineTransform(seq[:6]))
im.transform((100, 100), ImageTransform.ExtentTransform(seq[:4]))
im.transform((100, 100), ImageTransform.QuadTransform(seq[:8]))
im.transform((100, 100), ImageTransform.MeshTransform([(seq[:4], seq[:8])]))

print "ok"
