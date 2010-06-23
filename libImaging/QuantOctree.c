// Copyright (c) 2010 Oliver Tonnhofer <olt@bogosoft.com>, Omniscale
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


/*
This file implements a variation of the octree color quantization algorithm.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Quant.h"

typedef struct _ColorNode{
   unsigned long count;
   unsigned long r;
   unsigned long g;
   unsigned long b;
} *ColorNode;

typedef struct _ColorCube{
   int level;
   int rBits, gBits, bBits;
   int rWidth, gWidth, bWidth;
   int size;
   ColorNode nodes;
} *ColorCube;

static ColorCube
new_color_cube(int level) {
   int width;
   int r, g, b;
   ColorCube cube;
   ColorNode n;
   
   cube = malloc(sizeof(struct _ColorCube));
   if (!cube) return NULL;
   
   cube->level = level;
   // uniform cube only at this time
   cube->rBits = level;
   cube->gBits = level;
   cube->bBits = level;
   
   cube->rWidth = 1<<cube->rBits;
   cube->gWidth = 1<<cube->gBits;
   cube->bWidth = 1<<cube->bBits;
   
   cube->size = cube->rWidth * cube->gWidth * cube->bWidth;
   cube->nodes = calloc(cube->size, sizeof(struct _ColorNode));
   
   if (!cube->nodes) {
      free(cube);
      return NULL;
   }
   return cube;
}

static void
free_color_cube(ColorCube cube) {
   if (cube->nodes != NULL)
      free(cube->nodes);
   if (cube != NULL)
      free(cube);
}

static int
color_node_offset_pos(const ColorCube cube, int r, int g, int b) {
   int offset;
   offset = r;
   offset = offset<<cube->rBits | g;
   offset = offset<<cube->gBits | b;
   return offset;
}

static int
color_node_offset(const ColorCube cube, const Pixel *p) {
   int r = p->c.r>>(8-cube->rBits);
   int g = p->c.g>>(8-cube->gBits);
   int b = p->c.b>>(8-cube->bBits);
   return color_node_offset_pos(cube, r, g, b);
}


static ColorNode
color_node_from_cube(const ColorCube cube, const Pixel *p) {
   int offset = color_node_offset(cube, p);
   return &cube->nodes[offset];
}

static void
add_color_to_color_cube(const ColorCube cube, const Pixel *p) {
   ColorNode node = color_node_from_cube(cube, p);
   node->count += 1;
   node->r += p->c.r;
   node->g += p->c.g;
   node->b += p->c.b;
}

static long
count_used_color_nodes(const ColorCube cube) {
   long usedNodes = 0;
   int i;
   for (i=0; i < cube->size; i++) {
      if (cube->nodes[i].count > 0) {
         usedNodes += 1;
      }
   }
   return usedNodes;
}

static void
avg_color_from_color_node(const ColorNode node, Pixel *dst) {
   float count = node->count;
   dst->c.r = (int)(node->r / count);
   dst->c.g = (int)(node->g / count);
   dst->c.b = (int)(node->b / count);
}

static int
compare_node_count(const ColorNode a, const ColorNode b) {
   return b->count - a->count;
}

static ColorNode
create_color_cube_palette(const ColorCube cube) {
   ColorNode nodes;
   nodes = malloc(sizeof(struct _ColorNode)*cube->size);
   if (!nodes) return NULL;
   memcpy(nodes, cube->nodes, sizeof(struct _ColorNode)*cube->size);
   
   qsort(nodes, cube->size, sizeof(struct _ColorNode), 
         (int (*)(void const *, void const *))&compare_node_count);
   
   return nodes;
}

void add_node_values(ColorNode src, ColorNode dst) {
   dst->count += src->count;
   dst->r += src->r;
   dst->g += src->g;
   dst->b += src->b;
}

static ColorCube create_coarse_color_cube(const ColorCube cube, int level) {
   int r, g, b;
   int reduce;
   reduce = cube->level - level;
   ColorCube result = new_color_cube(level);
   if (!result) return NULL;

   for (r=0; r<cube->rWidth; r++) {
      for (g=0; g<cube->gWidth; g++) {
         for (b=0; b<cube->bWidth; b++) {
            int src_pos = color_node_offset_pos(cube, r, g, b);
            int dst_pos = color_node_offset_pos(result, r>>reduce, g>>reduce, b>>reduce);
            add_node_values(
               &cube->nodes[src_pos],
               &result->nodes[dst_pos]
            );
         }
      }
   }
   return result;
}

static void
set_lookup_value(const ColorCube cube, const Pixel *p, long value) {
   ColorNode node = color_node_from_cube(cube, p);
   node->count = value;
}

unsigned long
lookup_color(const ColorCube cube, const Pixel *p) {
   ColorNode node = color_node_from_cube(cube, p);
   return node->count;
}

static ColorCube
create_lookup_color_cube(
   const ColorCube cube,
   ColorNode palette,
   int nColors)
{
   ColorCube lookupCube;
   Pixel p;
   int i;
   lookupCube = malloc(sizeof(struct _ColorCube));
   if (!lookupCube) return NULL;
   memcpy(lookupCube, cube, sizeof(struct _ColorCube));
   lookupCube->nodes = calloc(cube->size, sizeof(struct _ColorNode));
   if (!lookupCube->nodes) {
      free(lookupCube);
      return NULL;
   }
   
   for (i=0; i<nColors; i++) {
      avg_color_from_color_node(&palette[i], &p);
      set_lookup_value(lookupCube, &p, i);
   }
   return lookupCube;
}

static Pixel *
create_palette_array(const ColorNode palette, unsigned int paletteLength) {
   Pixel *paletteArray;
   long i;
   
   paletteArray = malloc(sizeof(Pixel)*paletteLength);
   if (!paletteArray) return NULL;
   
   for (i=0; i<paletteLength; i++) {
      avg_color_from_color_node(&palette[i], &paletteArray[i]);
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
   ColorCube cube;
   ColorCube coarse_cube;
   ColorCube lookupCube;
   ColorNode paletteNodes;
   unsigned long *qp;
   long i;
   
   cube = new_color_cube(4);
   if (!cube) goto error_0;
   
   for (i=0; i<nPixels; i++) {
      add_color_to_color_cube(cube, &pixelData[i]);
   }
   
   // coarse_cube = create_coarse_color_cube(cube, 3);
   // cube = coarse_cube;
   
   paletteNodes = create_color_cube_palette(cube);
   if (!paletteNodes) goto error_1;
   
   lookupCube = create_lookup_color_cube(cube, paletteNodes, nQuantPixels);
   if (!lookupCube) goto error_2;
   
   qp = malloc(sizeof(Pixel)*nPixels);
   if (!qp) goto error_3;

   map_image_pixels(pixelData, nPixels, lookupCube, qp);
   
   *palette = create_palette_array(paletteNodes, nQuantPixels);
   if (!(*palette)) goto error_4;
   
   *quantizedPixels = qp;
   *paletteLength = nQuantPixels;
   
   free_color_cube(cube);
   free_color_cube(lookupCube);
   free(paletteNodes);
   return 1;

error_4:
   free(qp);
error_3:
   free_color_cube(lookupCube);
error_2:
   free(paletteNodes);
error_1:
   free_color_cube(cube);
error_0:
   return 0;
}
