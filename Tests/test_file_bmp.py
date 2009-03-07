from tester import *

from PIL import Image

def test_archive():
    import glob
    for file in glob.glob("../pil-archive/*.bmp"):
        try:
            im = Image.open(file)
            im.load()
        except:
            print "- failed to open", file

run()
