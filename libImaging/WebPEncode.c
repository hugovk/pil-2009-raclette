/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for WebP data
 *
 * history:
 * 2011-06-26 fl  created
 *
 * Copyright (c) Fredrik Lundh 2011.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#ifdef HAVE_LIBWEBP

#include "WebP.h"
#include "webp/encode.h"

int
ImagingWebPEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
  return 0;
}

#endif
