/*
 * The Python Imaging Library
 * $Id$
 *
 * imaging access objects
 *
 * Copyright (c) Fredrik Lundh 2009.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

/* use Tests/make_hash.py to calculate these values */
#define ACCESS_TABLE_SIZE 15
#define ACCESS_TABLE_HASH 8096

static struct ImagingAccessInstance access_table[ACCESS_TABLE_SIZE];
  
static inline UINT32
hash(const char* mode)
{
    UINT32 i = ACCESS_TABLE_HASH;
    while (*mode)
        i = ((i<<5) + i) ^ (UINT8) *mode++;
    return i % ACCESS_TABLE_SIZE;
}

static ImagingAccess
add_item(const char* mode)
{
    UINT32 i = hash(mode);
    /* printf("hash %s => %d\n", mode, i); */
    if (access_table[i].mode) {
        fprintf(stderr, "AccessInit: hash collision: %d for both %s and %s\n",
                i, mode, access_table[i].mode);
        exit(1);
    }
    access_table[i].mode = mode;
    return &access_table[i];
}

/* fetch individual pixel */

static void
get_pixel(Imaging im, int x, int y, void* color)
{
    char* out = color;

    /* generic pixel access*/

    if (im->image8) {
        out[0] = im->image8[y][x];
    } else {
        UINT8* p = (UINT8*) &im->image32[y][x];
        if (im->type == IMAGING_TYPE_UINT8 && im->bands == 2) {
            out[0] = p[0];
            out[1] = p[3];
            return;
        }
        memcpy(out, p, im->pixelsize);
    }
}

static void
get_pixel_8(Imaging im, int x, int y, void* color)
{
    char* out = color;
    out[0] = im->image8[y][x];
}

static void
get_pixel_16L(Imaging im, int x, int y, void* color)
{
    char* out = color;
    out[0] = im->image8[y][x+x+0];
    out[1] = im->image8[y][x+x+1];
}

static void
get_pixel_16B(Imaging im, int x, int y, void* color)
{
    char* out = color;
    out[0] = im->image8[y][x+x+1];
    out[1] = im->image8[y][x+x+0];
}

static void
get_pixel_32(Imaging im, int x, int y, void* color)
{
    INT32* out = color;
    out[0] = im->image32[y][x];
}

/* store individual pixel */

static void
put_pixel(Imaging im, int x, int y, const void* color)
{
    if (im->type == IMAGING_TYPE_SPECIAL)
        ImagingPutPixel(im, x, y, color);
    else if (im->image8)
        im->image8[y][x] = *((UINT8*) color);
    else
        im->image32[y][x] = *((INT32*) color);
}

void
ImagingAccessInit()
{
#define ADD(mode, get, put)                     \
    { ImagingAccess access = add_item(mode);    \
        access->get_pixel = get;                \
        access->put_pixel = put;                \
    }

    /* populate access table */
    ADD("1", get_pixel_8, put_pixel);
    ADD("L", get_pixel_8, put_pixel);
    ADD("LA", get_pixel, put_pixel);
    ADD("I", get_pixel_32, put_pixel);
    ADD("I;16", get_pixel_16L, put_pixel);
    ADD("I;16B", get_pixel_16B, put_pixel);
    ADD("F", get_pixel_32, put_pixel);
    ADD("P", get_pixel_8, put_pixel);
    ADD("PA", get_pixel, put_pixel);
    ADD("RGB", get_pixel_32, put_pixel);
    ADD("RGBA", get_pixel_32, put_pixel);
    ADD("RGBX", get_pixel_32, put_pixel);
    ADD("CMYK",get_pixel_32, put_pixel);
    ADD("YCbCr", get_pixel_32, put_pixel);
}

ImagingAccess
ImagingAccessNew(Imaging im)
{
    ImagingAccess access = &access_table[hash(im->mode)];
    if (im->mode[0] != access->mode[0] || strcmp(im->mode, access->mode) != 0)
        return ImagingError_ValueError("cannot access this mode");
    return access;
}

void
_ImagingAccessDelete(Imaging im, ImagingAccess access)
{

}
