from PIL import Image

im = Image.new("L", (100, 100))
im = Image.new("L", (100, 100), None)
im = Image.new("L", (100, 100), 0)
im = Image.new("L", (100, 100), "black")

print "ok"
