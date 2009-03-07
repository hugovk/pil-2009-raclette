#define COPYRIGHTINFO "\
PILusm, a gaussian blur and unsharp masking library for PIL\n\
By Kevin Cazabon, copyright 2003\n\
kevin_cazabon@hotmail.com\n\
kevin@cazabon.com\n\
\n\
This library is free software; you can redistribute it and/or\n\
modify it under the terms of the GNU Lesser General Public\n\
License as published by the Free Software Foundation; either\n\
version 2.1 of the License, or (at your option) any later version.\n\
\n\
This library is distributed in the hope that it will be useful,\n\
but WITHOUT ANY WARRANTY; without even the implied warranty of\n\
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU\n\
Lesser General Public License for more details.\n\
\n\
You should have received a copy of the GNU Lesser General Public\n\
License along with this library; if not, write to the Free Software\n\
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA\n\
"

/////////////////////////////////////////////////////////////////////////////
// includes
/////////////////////////////////////////////////////////////////////////////
#include "Python.h"
#include "Imaging.h"


/////////////////////////////////////////////////////////////////////////////
// version information: update this before compiling for the versions you're using
/////////////////////////////////////////////////////////////////////////////
#define PILUSMVERSION        "0.6.0"
#define PILVERSION          "1.1.3"
#define PYTHONVERSION       "2.2.0"

/////////////////////////////////////////////////////////////////////////////
// version history
/////////////////////////////////////////////////////////////////////////////
/*
0.6.0   fixed/improved float radius support (oops!)
        now that radius can be a float (properly), changed radius value to
            be an actual radius (instead of diameter).  So, you should get
            similar results from PIL_usm as from other paint programs when
            using the SAME values (no doubling of radius required any more).
            Be careful, this may "break" software if you had it set for 2x
            or 5x the radius as was recommended with earlier versions.
        made PILusm thread-friendly (release GIL before lengthly operations,
            and re-acquire it before returning to Python).  This makes a huge
            difference with multi-threaded applications on dual-processor
            or "Hyperthreading"-enabled systems (Pentium4, Xeon, etc.)

0.5.0   added support for float radius values!

0.4.0   tweaked gaussian curve calculation to be closer to consistent shape
            across a wide range of radius values

0.3.0   changed deviation calculation in gausian algorithm to be dynamic
        _gblur now adds 1 to the user-supplied radius before using it so
            that a value of "0" returns the original image instead of a
            black one.
        fixed handling of alpha channel in RGBX, RGBA images
        improved speed of gblur by reducing unnecessary checks and assignments

0.2.0   fixed L-mode image support

0.1.0   initial release
*/

/////////////////////////////////////////////////////////////////////////////
// known to-do list with current version
/////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////
// options / configuration
/////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////
// reference
/////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////
// structs
/////////////////////////////////////////////////////////////////////////////
typedef struct {
    PyObject_HEAD
    Imaging image;
} ImagingObject;


/////////////////////////////////////////////////////////////////////////////
// internal functions
/////////////////////////////////////////////////////////////////////////////
UINT8
clip (double in) {
  if (in >= 255.0) return (UINT8) 255;
  if (in <= 0.0) return (UINT8) 0;
  else return (UINT8) in;
}


int 
_gblur(Imaging im, Imaging imOut, float floatRadius, int channels, int padding) {
  float *maskData = NULL;
  double mult = 0.0;
  int y = 0;
  int x = 0;
  float z = 0;
  float sum = 0.0;
  float dev = 0.0;

  float *buffer = NULL;

  int *line = NULL;
  UINT8 *line8 = NULL;

  int pix = 0;
  float *newPixel = NULL;
  int channel = 0;
  int offset = 0;
  INT32 newPixelFinals;

  int radius = 0;
  float remainder = 0.0;

  ///////////////////////////////////////////////
  // do the gaussian blur
  ///////////////////////////////////////////////
  /*
  For a symmetrical gaussian blur, instead of doing a radius*radius matrix lookup,
  you get the EXACT same results by doing a radius*1 transform, followed by a 1*radius transform.
  This reduces the number of lookups exponentially (10 lookups per pixel for a radius of 5
  instead of 25 lookups).  So, we blur the lines first, then we blur the resulting columns.
  */

  // first, round radius off to the next higher integer and hold the remainder
  // this is used so we can support float radius values properly.
  remainder = floatRadius - ((int)floatRadius);
  floatRadius = (int)(floatRadius + 0.999999);

  // next, double the radius and offset by 2.0... that way "0" returns the original image instead of a black one.
  // we multiply it by 2.0 so that it is a true "radius", not a diameter (the results match other
  // paint programs closer that way too).
  radius = (int)((floatRadius * 2.0) + 2.0);

  // create the maskData for the gaussian curve
  maskData = new float[radius];
  for (x = 0; x < radius; x++) {
    z = (float(x + 2)/((float)radius));
    dev = 0.5 + (((float)(radius * radius)) * 0.001); // you can adjust this factor to change the shape/center-weighting of the gaussian
    maskData[x] = (float) pow((1.0 / sqrt(2.0 * 3.14159265359 * dev)), ((-(z - 1.0) * -(x - 1.0)) / (2.0 * dev)));
  }

  // if there's any remainder, multiply the first/last values in MaskData it.
  // this allows us to support float radius values.
  if (remainder > 0.0) {
    maskData[0] *= remainder;
    maskData[radius - 1] *= remainder;
  }

  for (x = 0; x < radius; x++) {
    // this is done separately now due to the correction for float radius values above
    sum += maskData[x];
  }

  for (int i = 0; i < radius; i++) {
    maskData[i] *= (1.0/sum);
    //printf("%f\n", maskData[i]); // to see the maskData values, if you're interested.
  }

  // create a temporary memory buffer for the data for the first pass
  // memset the buffer to 0 so we can use it directly with +=
  buffer = new float [im->xsize * im->ysize * channels];  // don't bother about alpha/padding
  
  if (buffer == NULL) {
    return -1;
  }

  Py_BEGIN_ALLOW_THREADS  // be nice to other threads while you go off to lala land

  memset(buffer, 0, sizeof(buffer));

  // perform a blur on each line, and place in the temporary storage buffer
  newPixel = new float[4];
  for (y = 0; y < im->ysize; y++) {
    if (channels == 1 && im->image8 != NULL) {
      line8 = (UINT8*) im->image8[y];
    }
    else {
      line = im->image32[y];
    }
    for (x = 0; x < im->xsize; x++) {
      newPixel[0] = newPixel[1] = newPixel[2] = newPixel[3] = 0;
      // for each neighbor pixel, factor in its value/weighting to the current pixel
      for (pix = 0; pix < radius; pix++) {
        // figure the offset of this neighbor pixel
        offset = (int) ((-((float)radius / 2.0) + (float)pix) + 0.5);
        if (x + offset < 0) offset = -x;
        else if (x + offset >= im->xsize) offset = im->xsize - x - 1;

        // add (neighbor pixel value * maskData[pix]) to the current pixel value
        if (channels == 1) {
          buffer[(y * im->xsize) + x] += ((float) ((UINT8*)&line8[x + offset])[0]) * (maskData[pix]);
        }
        else {
          for (channel = 0; channel < channels; channel++){
            buffer[(y * im->xsize * channels) + (x * channels) + channel] += ((float) ((UINT8*)&line[x + offset])[channel]) * (maskData[pix]);
          }
        }
      }
    }
  }

  // perform a blur on each column in the buffer, and place in the output image
  for (x = 0; x < im->xsize; x++) {
    for (y = 0; y < im->ysize; y++) {
      newPixel[0] = newPixel[1] = newPixel[2] = newPixel[3] = 0;
      // for each neighbor pixel, factor in its value/weighting to the current pixel
      for (pix = 0; pix < radius; pix++) {
        // figure the offset of this neighbor pixel
        offset = (int)(-((float)radius / 2.0) + (float)pix + 0.5);
        if (y + offset < 0) offset = -y;
        else if (y + offset >= im->ysize) offset = im->ysize - y - 1;

        // add (neighbor pixel value * maskData[pix]) to the current pixel value
        for (channel = 0; channel < channels; channel++){
          newPixel[channel] += (buffer[((y + offset) * im->xsize * channels) + (x * channels) + channel]) * (maskData[pix]);
        }
      }
      // if the image is RGBX or RGBA, copy the 4th channel data to newPixel, so it gets put in imOut
      if (strcmp(im->mode, "RGBX") == 0 || strcmp(im->mode, "RGBA") == 0) {
        newPixel[3] = ((UINT8*)&line[x + offset])[3];
      }
      // pack the channels into an INT32 so we can put them back in the PIL image
      newPixelFinals = 0;
      if (channels == 1) {
        newPixelFinals = clip(newPixel[0]);
      }
      else {  // for RGB, the fourth channel isn't used anyways, so just pack a 0 in there, this saves checking the mode for each pixel.
        // this doesn't work on little-endian machines... fix it!
        newPixelFinals = clip(newPixel[0]) | clip(newPixel[1]) << 8 | clip(newPixel[2]) << 16 | clip(newPixel[3]) << 24;
      }

      // set the resulting pixel in imOut
      if (channels == 1) {
        imOut->image8[y][x] = (UINT8) newPixelFinals;
      }
      else {
        imOut->image32[y][x] = newPixelFinals;   
      }
    }
  }
  free(newPixel);

  // free the buffer
  free(buffer);

  Py_END_ALLOW_THREADS  // get the GIL back so Python knows who you are

  // return 0 on success
  return 0;
}

/////////////////////////////////////////////////////////////////////////////
// Python callable functions
/////////////////////////////////////////////////////////////////////////////
static PyObject *
versions (PyObject *self, PyObject *args) {
  return Py_BuildValue ("sss", PILUSMVERSION, PYTHONVERSION, PILVERSION);
}

static PyObject *
about (PyObject *self, PyObject *args) {
  return Py_BuildValue("s", COPYRIGHTINFO);
}

static PyObject *
copyright (PyObject *self, PyObject *args) {
  return about(self, args);
}

static PyObject *
gblur (PyObject *self, PyObject *args) {
  long idIn = 0L;
  long idOut = 0L;

  Imaging im = NULL;
  Imaging imOut = NULL;

  float radius = 0.0;
  int result = 0;

  int channels = 0;
  int padding = 0;

  if (!PyArg_ParseTuple(args, "llf", &idIn, &idOut, &radius)) {
    return Py_BuildValue("is", -1, "ERROR: Could not parse argument tuple, check documentation.");
  }

  im = (Imaging) idIn;
  imOut = (Imaging) idOut;

  if (strcmp(im->mode, "RGB") == 0) {
    channels = 3;
    padding = 1;
  }
  else if (strcmp(im->mode, "RGBA") == 0) {
    channels = 3;
    padding = 1;
  }
  else if (strcmp(im->mode, "RGBX") == 0) {
    channels = 3;
    padding = 1;
  }
  else if (strcmp(im->mode, "CMYK") == 0) {
    channels = 4;
    padding = 0;
  }
  else if (strcmp(im->mode, "L") == 0) {
    channels = 1;
    padding = 0;
  }
  else {
    return Py_BuildValue("is", -1, "ERROR: only RGB, RGBA, RGBX, CMYK and L mode images supported.");
  }

  result = _gblur(im, imOut, radius, channels, padding);

  if (result == 0) return Py_BuildValue("is", 0, "");
  else return Py_BuildValue("is", result, "ERROR: unknown error occurred during blur operation.");

}

static PyObject *
usm (PyObject *self, PyObject *args) {
  long idIn = 0L;
  long idOut = 0L;
  float radius = 0.0;
  int percent = 0;
  int threshold = 0;

  Imaging im = NULL;
  Imaging imOut = NULL;

  int result = 0;
  int channel = 0;
  int channels = 0;
  int padding = 0;

  int x = 0;
  int y = 0;

  int *lineIn = NULL;
  int *lineOut = NULL;
  UINT8 *lineIn8 = NULL;
  UINT8 *lineOut8 = NULL;

  int diff = 0;

  INT32 newPixel = 0;

  if (!PyArg_ParseTuple(args, "llfii", &idIn, &idOut, &radius, &percent, &threshold)) {
    return Py_BuildValue("is", -1, "ERROR: Could not parse argument tuple, check documentation.");
  }

  im = (Imaging) idIn;
  imOut = (Imaging) idOut;

  if (strcmp(im->mode, "RGB") == 0) {
    channels = 3;
    padding = 1;
  }
  else if (strcmp(im->mode, "RGBA") == 0) {
    channels = 3;
    padding = 1;
  }
  else if (strcmp(im->mode, "RGBX") == 0) {
    channels = 3;
    padding = 1;
  }
  else if (strcmp(im->mode, "CMYK") == 0) {
    channels = 4;
    padding = 0;
  }
  else if (strcmp(im->mode, "L") == 0) {
    channels = 1;
    padding = 0;
  }
  else {
    return Py_BuildValue("is", -1, "ERROR: only RGB, RGBA, RGBX, CMYK and L mode images supported.");
  }

  /////////////////////////////////////
  // first, do a gaussian blur on the image, putting results in imOut temporarily
  /////////////////////////////////////
  result = _gblur(im, imOut, radius, channels, padding);
  if (result != 0) return Py_BuildValue("is", result, "ERROR: unknown error occured during _gblur portion of usm");

  /////////////////////////////////////
  // now, go through each pixel, compare "normal" pixel to blurred pixel.
  // if the difference is more than threshold values, apply the OPPOSITE 
  // correction to the amount of blur, multiplied by percent.
  /////////////////////////////////////

  Py_BEGIN_ALLOW_THREADS  // be nice to other threads while you go off to lala land

  for (y = 0; y < im->ysize; y++) {
    if (channels == 1) {
      lineIn8 = im->image8[y];
      lineOut8 = imOut->image8[y];
    }
    else {
      lineIn = im->image32[y];
      lineOut = imOut->image32[y];
    }
    for (x = 0; x < im->xsize; x++) {
      newPixel = 0;
      // compare in/out pixels, apply sharpening
      if (channels == 1) {
        diff = ((UINT8*)&lineIn8[x])[0] - ((UINT8*)&lineOut8[x])[0];
        if (abs(diff) > threshold) {
          // add the diff*percent to the original pixel
          imOut->image8[y][x] = clip((((UINT8*)&lineIn8[x])[0]) + (diff * ((float)percent)/100.0));
        }
        else {
          // newPixel is the same as imIn
          imOut->image8[y][x] = ((UINT8*)&lineIn8[x])[0];
        }
      }

      else {
        for (channel = 0; channel < channels; channel++){
          diff = (float) ((((UINT8*)&lineIn[x])[channel]) - (((UINT8*)&lineOut[x])[channel]));
          if (abs(diff) > threshold) {
            // add the diff*percent to the original pixel
            // this may not work for little-endian systems, fix it!
            newPixel = newPixel | clip ( (float)(((UINT8*)&lineIn[x])[channel]) + (diff * (((float)percent/100.0))) ) << (channel * 8);
          }
          else {
            // newPixel is the same as imIn
            // this may not work for little-endian systems, fix it!
            newPixel = newPixel | ((UINT8*)&lineIn[x])[channel] << (channel * 8);
          }
        }
        if (strcmp(im->mode, "RGBX") == 0 || strcmp(im->mode, "RGBA") == 0) {
          // preserve the alpha channel
          // this may not work for little-endian systems, fix it!
          newPixel = newPixel | ((UINT8*)&lineIn[x])[channel] << 24;
        }
        imOut->image32[y][x] = newPixel;  
      }
    }
  }

  Py_END_ALLOW_THREADS  // get the GIL back so Python knows who you are

  return Py_BuildValue("is", 0, "");
}

/////////////////////////////////////////////////////////////////////////////
// Python interface setup
/////////////////////////////////////////////////////////////////////////////
static PyMethodDef PILusm_methods[] = {
  // pyCMS info
  {"versions", versions, 1, ".versions()"},
  {"about", about, 1, ".about()"},
  {"copyright", copyright, 1, ".copyright()"},

  {"gblur", gblur, 1, ".gblur(imIn.im.id, imOut.im.id, radius)"},
  {"usm", usm, 1, ".usm(imIn.im.id, imOut.im.id, radius, percent, threshold)"},

  {NULL, NULL}
};


extern "C" {
  void initPILusm(void)
  {
    Py_InitModule("PILusm", PILusm_methods);
  }
}
