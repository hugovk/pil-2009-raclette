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
    UINT8* buffer;
    UINT8* ptr;
    uint8_t* output_data;
    size_t output_size;
    int y, stride;

    /* do this in state 0 */

    stride = state->xsize * 3;

    buffer = malloc(im->ysize * stride);
    if (!buffer) {
	state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    for (ptr = buffer, y = 0; y < state->ysize; ptr += stride, y++) {
        state->shuffle(ptr, (UINT8*) im->image[y + state->yoff] +
		       state->xoff * im->pixelsize, state->xsize);
    }

    output_size = WebPEncodeRGB(buffer, state->xsize, state->ysize, stride,
				75.f, &output_data);

    if (!output_size) {
	state->errcode = IMAGING_CODEC_BROKEN;
	return -1;
    }

    /* return data piecewise in state 1 */

    state->errcode = IMAGING_CODEC_END;

    ptr = buf;

    if (output_size < bytes) {
        memcpy(buf, output_data, output_size);
	ptr += output_size;
    }

    return ptr - buf;
}

#endif
