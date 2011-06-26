/*
 * The Python Imaging Library.
 * $Id$
 *
 * WebP decoder
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
#include "webp/decode.h"

int
ImagingWebPDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    WEBPSTATE* webpstate = state->context;

    return 0;
}

#endif
