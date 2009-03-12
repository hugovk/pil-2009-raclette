/*
 * Python Imaging Library
 * $Id: _pilwmf.c 321 2004-02-24 17:48:07Z fredrik $
 *
 * PIL WMF driver for Windows
 *
 * history:
 * 2004-02-22 fl   created (placable metafiles only)
 * 2004-02-24 fl   added support for enhanced metafiles; draw in dib section
 *
 * Copyright (c) 2004 by Fredrik Lundh.
 */

#include "Python.h"

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

#if 0
static void
windows_error(char *msg)
{
    LPVOID lpMsgBuf;
    fprintf(stderr, "Windows Error: %s\n", msg);
    fprintf(stderr, "  GetLastError() => %d\n", GetLastError());
    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER |
		  FORMAT_MESSAGE_FROM_SYSTEM,
		  NULL,
		  GetLastError(),
		  MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		  (LPTSTR) &lpMsgBuf,
		  0,
		  NULL 
                  );
    fprintf(stderr, "  FormatMessage() => %s\n", (char*) lpMsgBuf);
    LocalFree(lpMsgBuf);
}
#endif

#define GET32(p,o) ((DWORD*)(p+o))[0]

static PyObject *
_load(PyObject* self, PyObject* args)
{
    HBITMAP bitmap;
    HENHMETAFILE meta;
    BITMAPCOREHEADER core;
    HDC dc;
    RECT rect;
    PyObject* buffer = NULL;
    char* ptr;

    char* data;
    int datasize;
    int width, height;
    int x0, y0, x1, y1;
    if (!PyArg_ParseTuple(args, "s#(ii)(iiii):_load", &data, &datasize,
                          &width, &height, &x0, &x1, &y0, &y1))
        return NULL;

    /* step 1: copy metafile contents into METAFILE object */

    if (datasize > 22 && GET32(data, 0) == 0x9ac6cdd7) {

        /* placeable windows metafile (22-byte aldus header) */
        meta = SetWinMetaFileBits(datasize-22, data+22, NULL, NULL);

    } else if (datasize > 80 && GET32(data, 0) == 1 &&
               GET32(data, 40) == 0x464d4520) {

        /* enhanced metafile */
        meta = SetEnhMetaFileBits(datasize, data);

    } else {

        /* unknown meta format */
        meta = NULL;

    }

    if (!meta) {
        PyErr_SetString(PyExc_IOError, "cannot load metafile");
        return NULL;
    }

    /* step 2: create bitmap */

    core.bcSize = sizeof(core);
    core.bcWidth = width;
    core.bcHeight = height;
    core.bcPlanes = 1;
    core.bcBitCount = 24;

    dc = CreateCompatibleDC(NULL);

    bitmap = CreateDIBSection(
        dc, (BITMAPINFO*) &core, DIB_RGB_COLORS, &ptr, NULL, 0
        );

    if (!bitmap) {
        PyErr_SetString(PyExc_IOError, "cannot create bitmap");
        goto error;
    }

    if (!SelectObject(dc, bitmap)) {
        PyErr_SetString(PyExc_IOError, "cannot select bitmap");
        goto error;
    }

    /* step 3: render metafile into bitmap */

    rect.left = rect.top = 0;
    rect.right = width;
    rect.bottom = height;

    /* FIXME: make background transparent? configurable? */
    FillRect(dc, &rect, GetStockObject(WHITE_BRUSH));

    if (!PlayEnhMetaFile(dc, meta, &rect)) {
        PyErr_SetString(PyExc_IOError, "cannot render metafile");
        goto error;
    }

    /* step 4: extract bits from bitmap */

    GdiFlush();

    buffer = PyString_FromStringAndSize(ptr, height * ((width*3 + 3) & -4));

error:
    DeleteEnhMetaFile(meta);

    if (bitmap)
        DeleteObject(bitmap);

    DeleteDC(dc);

    return buffer;
}

static PyMethodDef _functions[] = {
    {"load", _load, 1},
    {NULL, NULL}
};

DL_EXPORT(void)
init_imagingwmf()
{
    Py_InitModule("_imagingwmf", _functions);
}
