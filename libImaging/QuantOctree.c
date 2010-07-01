/* Copyright (c) 2010 Oliver Tonnhofer <olt@bogosoft.com>, Omniscale
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
*/

/*
// This file implements a variation of the octree color quantization algorithm.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Quant.h"

typedef struct _ColorBucket{
   /* contains palette index when used for look up cube */
   unsigned long count;
   unsigned long r;
   unsigned long g;
   unsigned long b;
} *ColorBucket;

typedef struct _ColorCube{
   unsigned int level;
   unsigned int rBits, gBits, bBits;
   unsigned int rWidth, gWidth, bWidth;
   unsigned int rOffset, gOffset, bOffset;
   long size;
   ColorBucket buckets;
} *ColorCube;

static ColorCube
new_color_cube(int level) {
   ColorCube cube;
   
   cube = malloc(sizeof(struct _ColorCube));
   if (!cube) return NULL;
   
   cube->level = level;
   /* uniform cube only at this time */
   cube->rBits = level;
   cube->gBits = level;
   cube->bBits = level;
   
   /* the width of the cube for each dimension */
   cube->rWidth = 1<<cube->rBits;
   cube->gWidth = 1<<cube->gBits;
   cube->bWidth = 1<<cube->bBits;
   
   /* the offsets of each color */
   cube->rOffset = cube->rBits + cube->gBits;
   cube->gOffset = cube->gBits;
   cube->bOffset = 0;
   
   /* the number of color buckets */
   cube->size = cube->rWidth * cube->gWidth * cube->bWidth;
   cube->buckets = calloc(cube->size, sizeof(struct _ColorBucket));
   
   if (!cube->buckets) {
      free(cube);
      return NULL;
   }
   return cube;
}

static void
free_color_cube(ColorCube cube) {
   if (cube != NULL) {
      free(cube->buckets);
      free(cube);
   }
}

static long
color_bucket_offset_pos(const ColorCube cube,
   unsigned int r, unsigned int g, unsigned int b)
{
   return r<<cube->rOffset | g<<cube->gOffset | b<<cube->bOffset;
}

static long
color_bucket_offset(const ColorCube cube, const Pixel *p) {
   unsigned int r = p->c.r>>(8-cube->rBits);
   unsigned int g = p->c.g>>(8-cube->gBits);
   unsigned int b = p->c.b>>(8-cube->bBits);
   return color_bucket_offset_pos(cube, r, g, b);
}

static ColorBucket
color_bucket_from_cube(const ColorCube cube, const Pixel *p) {
   unsigned int offset = color_bucket_offset(cube, p);
   return &cube->buckets[offset];
}

static void
add_color_to_color_cube(const ColorCube cube, const Pixel *p) {
   ColorBucket bucket = color_bucket_from_cube(cube, p);
   bucket->count += 1;
   bucket->r += p->c.r;
   bucket->g += p->c.g;
   bucket->b += p->c.b;
}

static long
count_used_color_buckets(const ColorCube cube) {
   long usedBuckets = 0;
   long i;
   for (i=0; i < cube->size; i++) {
      if (cube->buckets[i].count > 0) {
         usedBuckets += 1;
      }
   }
   return usedBuckets;
}

static void
avg_color_from_color_bucket(const ColorBucket bucket, Pixel *dst) {
   float count = bucket->count;
   dst->c.r = (int)(bucket->r / count);
   dst->c.g = (int)(bucket->g / count);
   dst->c.b = (int)(bucket->b / count);
}

static int
compare_bucket_count(const ColorBucket a, const ColorBucket b) {
   return b->count - a->count;
}

static ColorBucket
create_sorted_color_palette(const ColorCube cube) {
   ColorBucket buckets;
   buckets = malloc(sizeof(struct _ColorBucket)*cube->size);
   if (!buckets) return NULL;
   memcpy(buckets, cube->buckets, sizeof(struct _ColorBucket)*cube->size);
   
   qsort(buckets, cube->size, sizeof(struct _ColorBucket), 
         (int (*)(void const *, void const *))&compare_bucket_count);
   
   return buckets;
}

void add_bucket_values(ColorBucket src, ColorBucket dst) {
   dst->count += src->count;
   dst->r += src->r;
   dst->g += src->g;
   dst->b += src->b;
}

/* expand or shrink a given cube to level */
static ColorCube copy_color_cube(const ColorCube cube, unsigned int level) {
   unsigned int r, g, b;
   long src_pos, dst_pos;
   unsigned int src_reduce, dst_reduce;
   unsigned int width;
   ColorCube result;
   
   result = new_color_cube(level);
   if (!result) return NULL;
   
   if (cube->level > level) {
      dst_reduce = cube->level - level;
      src_reduce = 0;
      width = cube->rWidth;
   } else {
      dst_reduce = 0;
      src_reduce = level - cube->level;
      width = result->rWidth;
   }
   for (r=0; r<width; r++) {
      for (g=0; g<width; g++) {
         for (b=0; b<width; b++) {
            src_pos = color_bucket_offset_pos(cube,
                                            r>>src_reduce,
                                            g>>src_reduce,
                                            b>>src_reduce);
            dst_pos = color_bucket_offset_pos(result,
                                            r>>dst_reduce,
                                            g>>dst_reduce,
                                            b>>dst_reduce);
            add_bucket_values(
               &cube->buckets[src_pos],
               &result->buckets[dst_pos]
            );
         }
      }
   }
   return result;
}

void
subtract_color_buckets(ColorCube cube, ColorBucket buckets, long nBuckets) {
   ColorBucket minuend, subtrahend;
   long i;
   Pixel p;
   for (i=0; i<nBuckets; i++) {
      subtrahend = &buckets[i];
      avg_color_from_color_bucket(subtrahend, &p);
      minuend = color_bucket_from_cube(cube, &p);
      minuend->count -= subtrahend->count;
      minuend->r -= subtrahend->r;
      minuend->g -= subtrahend->g;
      minuend->b -= subtrahend->b;
   }
}

static void
set_lookup_value(const ColorCube cube, const Pixel *p, long value) {
   ColorBucket bucket = color_bucket_from_cube(cube, p);
   bucket->count = value;
}

unsigned long
lookup_color(const ColorCube cube, const Pixel *p) {
   ColorBucket bucket = color_bucket_from_cube(cube, p);
   return bucket->count;
}

static ColorCube
create_lookup_color_cube(
   const ColorCube cube,
   ColorBucket palette,
   int nColors)
{
   ColorCube lookupCube;
   Pixel p;
   int i;

   lookupCube = new_color_cube(cube->level);
   if (!lookupCube) return NULL;
   
   for (i=0; i<nColors; i++) {
      avg_color_from_color_bucket(&palette[i], &p);
      set_lookup_value(lookupCube, &p, i);
   }
   return lookupCube;
}


void add_lookup_buckets(ColorCube cube, ColorBucket palette, long nColors, long offset) {
   long i;
   Pixel p;
   for (i=offset; i<offset+nColors; i++) {
      avg_color_from_color_bucket(&palette[i], &p);
      set_lookup_value(cube, &p, i);
   }
}

ColorBucket
combined_palette(ColorBucket bucketsA, long nBucketsA, ColorBucket bucketsB, long nBucketsB) {
   ColorBucket result;
   result = malloc(sizeof(struct _ColorBucket)*(nBucketsA+nBucketsB));
   memcpy(result, bucketsA, sizeof(struct _ColorBucket) * nBucketsA);
   memcpy(&result[nBucketsA], bucketsB, sizeof(struct _ColorBucket) * nBucketsB);
   return result;
}


static Pixel *
create_palette_array(const ColorBucket palette, unsigned int paletteLength) {
   Pixel *paletteArray;
   unsigned int i;
   
   paletteArray = malloc(sizeof(Pixel)*paletteLength);
   if (!paletteArray) return NULL;
   
   for (i=0; i<paletteLength; i++) {
      avg_color_from_color_bucket(&palette[i], &paletteArray[i]);
   }
   return paletteArray;
}


static void
map_image_pixels(const Pixel *pixelData,
                 unsigned long nPixels,
                 const ColorCube lookupCube,
                 unsigned long *pixelArray)
{
   long i;
   for (i=0; i<nPixels; i++) {
      pixelArray[i] = lookup_color(lookupCube, &pixelData[i]);
   }
}


int quantize_octree(Pixel *pixelData,
          unsigned long nPixels,
          unsigned long nQuantPixels,
          Pixel **palette,
          unsigned long *paletteLength,
          unsigned long **quantizedPixels,
          int kmeans)
{
   ColorCube fineCube = NULL;
   ColorCube coarseCube = NULL;
   ColorCube lookupCube = NULL;
   ColorCube coarseLookupCube = NULL;
   ColorBucket paletteBucketsCoarse = NULL;
   ColorBucket paletteBucketsFine = NULL;
   ColorBucket paletteBuckets = NULL;
   unsigned long *qp = NULL;
   long i;
   long nCoarseColors, nFineColors, nAlreadySubtracted;
   
   /*
   Create two color cubes, one fine grained with 16x16x16=4096
   colors buckets and a coarse with 4*4*4=64 color buckets.
   The coarse one guarantes that there are color buckets available for
   the whole color range (assuming nQuantPixels > 64).
   
   For a quantization to 256 colors all 64 coarse colors will be used
   plus the 192 most used color buckets from the fine color cube.
   The average of all colors within one bucket is used as the actual
   color for that bucket.
   */
   
   /* create fine cube */
   fineCube = new_color_cube(4);
   if (!fineCube) goto error;
   for (i=0; i<nPixels; i++) {
      add_color_to_color_cube(fineCube, &pixelData[i]);
   }
   
   /* create coarse cube */
   coarseCube = copy_color_cube(fineCube, 2);
   if (!coarseCube) goto error;
   nCoarseColors = count_used_color_buckets(coarseCube);
   
   /* limit to nQuantPixels */
   if (nCoarseColors > nQuantPixels)
      nCoarseColors = nQuantPixels;
   
   /* how many space do we have in our palette for fine colors? */
   nFineColors = nQuantPixels - nCoarseColors;
   
   /* create fine color palette */
   paletteBucketsFine = create_sorted_color_palette(fineCube);
   if (!paletteBucketsFine) goto error;
   
   /* remove the used fine colors from the coarse cube */
   subtract_color_buckets(coarseCube, paletteBucketsFine, nFineColors);
   
   /* did the substraction cleared one or more coarse bucket? */
   while (nCoarseColors > count_used_color_buckets(coarseCube)) {
      /* then we can use the free buckets for fine colors */
      nAlreadySubtracted = nFineColors;
      nCoarseColors = count_used_color_buckets(coarseCube);
      nFineColors = nQuantPixels - nCoarseColors;
      subtract_color_buckets(coarseCube, &paletteBucketsFine[nAlreadySubtracted],
                             nFineColors-nAlreadySubtracted);
   }
   
   /* create our palette buckets with fine and coarse combined */
   paletteBucketsCoarse = create_sorted_color_palette(coarseCube);
   if (!paletteBucketsCoarse) goto error;
   paletteBuckets = combined_palette(paletteBucketsCoarse, nCoarseColors,
                                     paletteBucketsFine, nFineColors);
   
   free(paletteBucketsFine);
   paletteBucketsFine = NULL;
   free(paletteBucketsCoarse);
   paletteBucketsCoarse = NULL;
   
   /* add all coarse colors to our coarse lookup cube. */
   coarseLookupCube = new_color_cube(2);
   if (!coarseLookupCube) goto error;
   add_lookup_buckets(coarseLookupCube, paletteBuckets, nCoarseColors, 0);
   
   /* expand coarse cube (64) to larger fine cube (4k). the value of each
      coarse bucket is then present in the according 64 fine buckets. */
   lookupCube = copy_color_cube(coarseLookupCube, 4);
   if (!lookupCube) goto error;
   
   /* add fine colors to the lookup cube */
   add_lookup_buckets(lookupCube, paletteBuckets, nFineColors, nCoarseColors);
   
   /* create result pixles and map palatte indices */
   qp = malloc(sizeof(Pixel)*nPixels);
   if (!qp) goto error;
   map_image_pixels(pixelData, nPixels, lookupCube, qp);
   
   /* convert palette buckets to RGB pixel palette */
   *palette = create_palette_array(paletteBuckets, nQuantPixels);
   if (!(*palette)) goto error;
   
   *quantizedPixels = qp;
   *paletteLength = nQuantPixels;
   
   free_color_cube(coarseCube);
   free_color_cube(fineCube);
   free_color_cube(lookupCube);
   free_color_cube(coarseLookupCube);
   free(paletteBuckets);
   return 1;

error:
   /* everything is initialized to NULL
      so we are safe to call free */
   free(qp);
   free_color_cube(lookupCube);
   free_color_cube(coarseLookupCube);
   free(paletteBucketsCoarse);
   free(paletteBucketsFine);
   free_color_cube(coarseCube);
   free_color_cube(fineCube);
   return 0;
}
