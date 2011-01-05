import PIL
import PIL.Image

import glob, os

for file in glob.glob("../pil-archive/*"):
    f, e = os.path.splitext(file)
    if e in [".txt", ".ttf", ".otf", ".zip"]:
        continue
    try:
        im = PIL.Image.open(file)
    except IOError, v:
        print "-", "failed to identify", file, "-", v
    else:
        if e == ".exif":
            try:
                info = im._getexif()
            except KeyError, v:
                print "-", "failed to get exif info from", file, "-", v
        try:
            im.load()
        except IOError, v:
            print "-", "failed to open", file, "-", v

print "ok"
