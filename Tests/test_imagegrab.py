from tester import *

from PIL import Image
try:
    from PIL import ImageGrab
except ImportError, v:
    skip(v)

success()
