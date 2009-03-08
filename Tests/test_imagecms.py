from tester import *

from PIL import Image
try:
    from PIL import ImageCms
except ImportError:
    skip()

cmyk = "Tests/icc/CMY.icm"
srgb = "Tests/icc/sRGB.icm"
ycc = "Tests/icc/YCC709.icm"

def test_sanity():

    # just check that everything's there
    ImageCms.applyTransform
    ImageCms.buildProofTransform
    ImageCms.buildProofTransformFromOpenProfiles
    ImageCms.buildTransform
    ImageCms.buildTransformFromOpenProfiles
    ImageCms.createProfile
    ImageCms.getDefaultIntent
    ImageCms.getOpenProfile
    ImageCms.getProfileInfo
    ImageCms.getProfileName
    ImageCms.isIntentSupported
    ImageCms.profileToProfile

    # some smoke tests
    t = ImageCms.buildTransform(srgb, srgb, "RGB", "RGB")
    assert_equal(t.inputMode, "RGB")
    assert_equal(t.outputMode, "RGB")
    assert_true(hasattr(t, "transform"))

    i = ImageCms.applyTransform(lena(), t)

    p = ImageCms.createProfile("sRGB")
    o = ImageCms.getOpenProfile(srgb)
    t = ImageCms.buildTransformFromOpenProfiles(p, o, "RGB", "RGB")

    p = ImageCms.getOpenProfile(srgb)
    assert_equal(ImageCms.getProfileName(p), '{no name}\n')
    assert_equal(ImageCms.getProfileInfo(p), 'White point near 8838K\r\n\r\n\n')
    # assert_equal(ImageCms.getDefaultIntent(p), 0) # FIXME
    assert_equal(ImageCms.isIntentSupported(p, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC, ImageCms.DIRECTION_INPUT), -1)

success()
