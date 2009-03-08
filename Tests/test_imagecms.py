from tester import *

from PIL import Image
try:
    from PIL import ImageCms
except ImportError:
    skip()

SRGB = "Tests/icc/sRGB.icm"

def test_sanity():

    # basic smoke test.
    # this mostly follows the cms_test outline.
    assert_exception(ImageCms.PyCMSError, lambda: ImageCms.profileToProfile(lena(), "foo", "bar")) # IOError would make a bit more sense

    i = ImageCms.profileToProfile(lena(), SRGB, SRGB)
    assert_image(i, "RGB", (128, 128))

    t = ImageCms.buildTransform(SRGB, SRGB, "RGB", "RGB")
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "RGB", (128, 128))

    p = ImageCms.createProfile("sRGB")
    o = ImageCms.getOpenProfile(SRGB)
    t = ImageCms.buildTransformFromOpenProfiles(p, o, "RGB", "RGB")
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "RGB", (128, 128))

    t = ImageCms.buildProofTransform(SRGB, SRGB, SRGB, "RGB", "RGB")
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "RGB", (128, 128))

    # FIXME: getProfileName et al crash if given a profile handle
    assert_equal(ImageCms.getProfileName(SRGB).strip(),
                 'IEC 61966-2.1 Default RGB colour space - sRGB')
    assert_equal(ImageCms.getProfileInfo(SRGB).splitlines(),
                 ['sRGB IEC61966-2.1', '',
                  'Copyright (c) 1998 Hewlett-Packard Company', '',
                  'WhitePoint : D65 (daylight)', '',
                  'Tests/icc/sRGB.icm'])
    assert_equal(ImageCms.getDefaultIntent(SRGB), 0)
    assert_equal(ImageCms.isIntentSupported(
            SRGB, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC,
            ImageCms.DIRECTION_INPUT), 1)
