import tester

from PIL import Image
try:
    from PIL import ImageQt
except ImportError, v:
    tester.skip(v)

