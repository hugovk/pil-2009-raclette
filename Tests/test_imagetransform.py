from PIL import Image
from PIL import ImageTransform

ImageTransform.AffineTransform((1, 2, 3, 4, 5, 6))
ImageTransform.ExtentTransform((1, 2, 3, 4))
ImageTransform.QuadTransform((1, 2, 3, 4, 5, 6, 7, 8))
ImageTransform.MeshTransform(((1, 2, 3, 4), (5, 6, 7, 8, 9, 10, 11, 12)))

print "ok"
