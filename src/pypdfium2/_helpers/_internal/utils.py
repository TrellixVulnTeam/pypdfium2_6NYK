# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

import copy
import ctypes
import pypdfium2._pypdfium as pdfium
from pypdfium2._helpers._internal import consts


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


def get_struct_slots(struct):
    return copy.copy(struct.__slots__)


def image_metadata_to_str(metadata, pad=""):
    imageinfo_maps = {"colorspace": consts.ColorspaceToStr}
    as_str = ""
    nl = ""
    for attr in get_struct_slots(pdfium.FPDF_IMAGEOBJ_METADATA):
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


def is_input_buffer(buf):
    """
    Returns:
        bool: True if the given object implements the methods ``seek()``, ``tell()``, ``read()``, and ``readinto()``. False otherwise.
    """
    return all( callable(getattr(buf, a, None)) for a in ("seek", "tell", "read", "readinto") )
