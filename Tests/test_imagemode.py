from PIL import Image
from PIL import ImageMode

ImageMode.getmode("1")
ImageMode.getmode("L")
ImageMode.getmode("P")
ImageMode.getmode("RGB")
ImageMode.getmode("I")
ImageMode.getmode("F")

m = ImageMode.getmode("1")
assert m.mode == "1"
assert m.bands == ("1",)
assert m.basemode == "L"
assert m.basetype == "L"

m = ImageMode.getmode("RGB")
assert m.mode == "RGB"
assert m.bands == ("R", "G", "B")
assert m.basemode == "RGB"
assert m.basetype == "L"

print "ok"
