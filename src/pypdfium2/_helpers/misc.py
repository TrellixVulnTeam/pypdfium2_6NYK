# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

# TODO clean up namespace, make many members private

import enum
import copy
import ctypes
from collections import namedtuple
import pypdfium2._pypdfium as pdfium


class PdfiumError (RuntimeError):
    """ An exception from the PDFium library, detected by function return code. """
    pass


class FileAccessMode (enum.Enum):
    """ File access modes. """
    NATIVE = 1  #: :func:`.FPDF_LoadDocument`       - Let PDFium manage file access in C/C++
    BUFFER = 2  #: :func:`.FPDF_LoadCustomDocument` - Pass data to PDFium incrementally from Python file buffer
    BYTES  = 3  #: :func:`.FPDF_LoadMemDocument64`  - Load data into memory and pass it to PDFium at once


class RenderOptimizeMode (enum.Enum):
    """ Page rendering optimization modes. """
    LCD_DISPLAY = 1  #: Optimize for LCD displays (via subpixel rendering).
    PRINTING    = 2  #: Optimize for printing.


# TODO rename to PdfOutlineItem and move to document.py
OutlineItem = namedtuple("OutlineItem", "level title is_closed n_kids page_index view_mode view_pos")
"""
Bookmark information.

Parameters:
    level (int):
        Number of parent items.
    title (str):
        String of the bookmark.
    is_closed (bool):
        True if child items shall be collapsed, False if they shall be expanded.
        None if the item has no descendants (i. e. ``n_kids == 0``).
    n_kids (int):
        Absolute number of child items, according to the PDF.
    page_index (int | None):
        Zero-based index of the page the bookmark points to.
        May be None if the bookmark has no target page (or it could not be determined).
    view_mode (int):
        A view mode constant (:data:`PDFDEST_VIEW_*`) defining how the coordinates of *view_pos* shall be interpreted.
    view_pos (typing.Sequence[float]):
        Target position on the page the viewport should jump to when the bookmark is clicked.
        It is a sequence of :class:`float` values in PDF canvas units.
        Depending on *view_mode*, it can contain between 0 and 4 coordinates.
"""


def color_tohex(color, rev_byteorder):
    """
    Convert an RGBA color specified by 4 integers ranging from 0 to 255 to a single 32-bit integer as required by PDFium.
    If using regular byte order, the output format will be ARGB. If using reversed byte order, it will be ABGR.
    """
    
    if len(color) != 4:
        raise ValueError("Color must consist of exactly 4 values.")
    if not all(0 <= c <= 255 for c in color):
        raise ValueError("Color value exceeds boundaries.")
    
    r, g, b, a = color
    
    # color is interpreted differently with FPDF_REVERSE_BYTE_ORDER (perhaps inadvertently?)
    if rev_byteorder:
        channels = (a, b, g, r)
    else:
        channels = (a, r, g, b)
    
    c_color = 0
    shift = 24
    for c in channels:
        c_color |= c << shift
        shift -= 8
    
    return c_color


# TODO move some components to private _utils.py file


def get_functype(struct, funcname):
    """
    Parameters:
        struct (ctypes.Structure): A structure (e. g. ``FPDF_FILEWRITE``).
        funcname (str): Name of the callback function to implement (e. g. ``WriteBlock``).
    Returns:
        A :func:`ctypes.CFUNCTYPE` instance to wrap the callback function.
        For some reason, this is not done automatically, although the information is present in the bindings file.
        This is a convenience function to retrieve the declaration.
    """
    return {k: v for k, v in struct._fields_}[funcname]


def get_slots(struct):
    return copy.copy(struct.__slots__)


def image_metadata_to_str(metadata, pad=""):
    imageinfo_maps = {"colorspace": ColorspaceToStr}
    as_str = ""
    nl = ""
    for attr in get_slots(pdfium.FPDF_IMAGEOBJ_METADATA):
        value = getattr(metadata, attr)
        if attr in imageinfo_maps:
            value = imageinfo_maps[attr].get(value, "PDFium constant %s" % value)
        as_str += nl + pad + "%s: %s" % (attr, value)
        nl = "\n"
    return as_str


class _buffer_reader:
    
    def __init__(self, buffer):
        self.buffer = buffer
    
    def __call__(self, _, position, p_buf, size):
        c_buf = ctypes.cast(p_buf, ctypes.POINTER(ctypes.c_char * size))
        self.buffer.seek(position)
        self.buffer.readinto(c_buf.contents)
        return 1


def get_bufaccess(buffer):
    """
    Acquire an :class:`FPDF_FILEACCESS` interface for a byte buffer.
    
    Returns:
        (FPDF_FILEACCESS, tuple): PDFium file access interface, and accompanying data that needs to be held in memory.
    """
    
    buffer.seek(0, 2)
    file_len = buffer.tell()
    buffer.seek(0)
    
    access = pdfium.FPDF_FILEACCESS()
    access.m_FileLen = file_len
    access.m_GetBlock = get_functype(pdfium.FPDF_FILEACCESS, "m_GetBlock")( _buffer_reader(buffer) )
    access.m_Param = None
    
    to_hold = (access.m_GetBlock, buffer)
    
    return access, to_hold


def is_input_buffer(maybe_buffer):
    """
    Returns:
        bool: True if the given object implements the methods ``seek()``, ``tell()``, ``read()``, and ``readinto()``. False otherwise.
    """
    return all( callable(getattr(maybe_buffer, a, None)) for a in ("seek", "tell", "read", "readinto") )


def _invert_dict(dictionary):
    """
    Returns:
        A copy of *dictionary*, with inverted keys and values.
    """
    return {v: k for k, v in dictionary.items()}


#: Get the number of channels for a PDFium bitmap format constant.
BitmapTypeToNChannels = {
    pdfium.FPDFBitmap_Gray: 1,
    pdfium.FPDFBitmap_BGR:  3,
    pdfium.FPDFBitmap_BGRA: 4,
    pdfium.FPDFBitmap_BGRx: 4,
}

#: Convert a PDFium bitmap format constant to string, assuming regular byte order.
BitmapTypeToStr = {
    pdfium.FPDFBitmap_Gray: "L",
    pdfium.FPDFBitmap_BGR:  "BGR",
    pdfium.FPDFBitmap_BGRA: "BGRA",
    pdfium.FPDFBitmap_BGRx: "BGRX",
}

#: Convert a PDFium bitmap format constant to string, assuming reversed byte order.
BitmapTypeToStrReverse = {
    pdfium.FPDFBitmap_Gray: "L",
    pdfium.FPDFBitmap_BGR:  "RGB",
    pdfium.FPDFBitmap_BGRA: "RGBA",
    pdfium.FPDFBitmap_BGRx: "RGBX",
}

#: Convert a PDFium color space constant to string.
ColorspaceToStr = {
    pdfium.FPDF_COLORSPACE_UNKNOWN:    "?",
    pdfium.FPDF_COLORSPACE_DEVICEGRAY: "DeviceGray",
    pdfium.FPDF_COLORSPACE_DEVICERGB:  "DeviceRGB",
    pdfium.FPDF_COLORSPACE_DEVICECMYK: "DeviceCMYK",
    pdfium.FPDF_COLORSPACE_CALGRAY:    "CalGray",
    pdfium.FPDF_COLORSPACE_CALRGB:     "CalRGB",
    pdfium.FPDF_COLORSPACE_LAB:        "Lab",
    pdfium.FPDF_COLORSPACE_ICCBASED:   "ICCBased",
    pdfium.FPDF_COLORSPACE_SEPARATION: "Separation",
    pdfium.FPDF_COLORSPACE_DEVICEN:    "DeviceN",
    pdfium.FPDF_COLORSPACE_INDEXED:    "Indexed",  # i. e. palettized
    pdfium.FPDF_COLORSPACE_PATTERN:    "Pattern",
}

#: Convert a PDFium view mode constant (:attr:`PDFDEST_VIEW_*`) to string.
ViewmodeToStr = {
    pdfium.PDFDEST_VIEW_UNKNOWN_MODE: "?",
    pdfium.PDFDEST_VIEW_XYZ:   "XYZ",
    pdfium.PDFDEST_VIEW_FIT:   "Fit",
    pdfium.PDFDEST_VIEW_FITH:  "FitH",
    pdfium.PDFDEST_VIEW_FITV:  "FitV",
    pdfium.PDFDEST_VIEW_FITR:  "FitR",
    pdfium.PDFDEST_VIEW_FITB:  "FitB",
    pdfium.PDFDEST_VIEW_FITBH: "FitBH",
    pdfium.PDFDEST_VIEW_FITBV: "FitBV",
}

#: Convert a PDFium error constant (:attr:`FPDF_ERR_*`) to string.
ErrorToStr = {
    pdfium.FPDF_ERR_SUCCESS:  "Success",
    pdfium.FPDF_ERR_UNKNOWN:  "Unknown error",
    pdfium.FPDF_ERR_FILE:     "File access error",
    pdfium.FPDF_ERR_FORMAT:   "Data format error",
    pdfium.FPDF_ERR_PASSWORD: "Incorrect password error",
    pdfium.FPDF_ERR_SECURITY: "Unsupported security scheme error",
    pdfium.FPDF_ERR_PAGE:     "Page not found or content error",
}

#: Convert a PDFium object type constant (:attr:`FPDF_PAGEOBJ_*`) to string.
ObjectTypeToStr = {
    pdfium.FPDF_PAGEOBJ_UNKNOWN: "?",
    pdfium.FPDF_PAGEOBJ_TEXT:    "text",
    pdfium.FPDF_PAGEOBJ_PATH:    "path",
    pdfium.FPDF_PAGEOBJ_IMAGE:   "image",
    pdfium.FPDF_PAGEOBJ_SHADING: "shading",
    pdfium.FPDF_PAGEOBJ_FORM:    "form",
}

#: Convert an object type string to a PDFium constant. Inversion of :data:`.ObjectTypeToStr`.
ObjectTypeToConst = _invert_dict(ObjectTypeToStr)

#: Convert a rotation value in degrees to a PDFium constant.
RotationToConst = {
    0:   0,
    90:  1,
    180: 2,
    270: 3,
}

#: Convert a PDFium rotation constant to a value in degrees. Inversion of :data:`.RotationToConst`.
RotationToDegrees = _invert_dict(RotationToConst)
