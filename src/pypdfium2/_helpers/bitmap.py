# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

__all__ = ["PdfBitmap", "PdfBitmapInfo"]

import logging
import ctypes
import weakref
from collections import namedtuple
import pypdfium2._pypdfium as pdfium
from pypdfium2._helpers.misc import (
    PdfiumError,
    color_tohex,
    BitmapTypeToNChannels,
    BitmapTypeToStr,
    BitmapTypeToStrReverse,
)

logger = logging.getLogger(__name__)

try:
    import PIL.Image
except ImportError:
    PIL = None

try:
    import numpy
except ImportError:
    numpy = None


PdfBitmapInfo = namedtuple("PdfBitmapInfo", "width height stride format rev_byteorder n_channels mode")
"""
TODO
"""


class PdfBitmap:
    """
    Bitmap helper class.
    
    Hint:
        This class provides built-in converters (including :meth:`.to_pil`, :meth:`.to_numpy`) that may be used to create a different representation of the bitmap.
        Converters can be applied on :class:`.PdfBitmap` objects either as bound method (``bitmap.to_*()``), or as function (``PdfBitmap.to_*(bitmap)``)
        The second pattern is useful for API methods that need to apply a caller-provided converter (e. g. :meth:`.PdfDocument.render`)
    
    .. _PIL Modes: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
    
    Attributes:
        raw (FPDF_BITMAP):
            The underlying PDFium bitmap handle.
        buffer (ctypes.c_ubyte):
            A ctypes array representation of the pixel data (each item is an unsigned byte, i. e. a number ranging from 0 to 255).
        width (int):
            Width of the bitmap (horizontal size).
        height (int):
            Height of the bitmap (vertical size).
        stride (int):
            Number of bytes per line in the buffer.
            Depending on how the bitmap was created, there may be a padding of unused bytes at the end of each line, so this value can be greater than ``width * n_channels``.
        mode (str):
            The bitmap format as string (see `PIL Modes`_).
        TODO
    """
    
    def __init__(
            self,
            raw,
            buffer,
            width,
            height,
            stride,
            format,
            rev_byteorder,
            needs_free,
        ):
        self.raw = raw
        self.buffer = buffer
        self.width = width
        self.height = height
        self.stride = stride
        self.format = format
        self.rev_byteorder = rev_byteorder
        self.n_channels = BitmapTypeToNChannels[self.format]
        if self.rev_byteorder:
            self.mode = BitmapTypeToStrReverse[self.format]
        else:
            self.mode = BitmapTypeToStr[self.format]
        
        self._finalizer = None
        if needs_free:
            self._finalizer = weakref.finalize(self.buffer, self._static_close, self.raw)
    
    @staticmethod
    def _static_close(raw):
        # logger.debug("Closing bitmap")
        pdfium.FPDFBitmap_Destroy(raw)
    
    
    def get_info(self):
        """
        TODO
        """
        return PdfBitmapInfo(
            width = self.width,
            height = self.height,
            stride = self.stride,
            format = self.format,
            rev_byteorder = self.rev_byteorder,
            n_channels = self.n_channels,
            mode = self.mode,
        )
    
    
    @classmethod
    def from_raw(cls, raw, rev_byteorder=False, ex_buffer=None):
        """
        Construct a :class:`.PdfBitmap` wrapper around a raw PDFium bitmap handle.
        
        Parameters:
            raw (FPDF_BITMAP):
                PDFium bitmap handle.
            rev_byteorder (bool):
                Whether the bitmap uses reverse byte order.
            ex_buffer (ctypes.c_ubyte | None):
                If the bitmap was created from a buffer allocated by Python/ctypes, pass in the ctypes array to keep it referenced.
        """
        
        width = pdfium.FPDFBitmap_GetWidth(raw)
        height = pdfium.FPDFBitmap_GetHeight(raw)
        format = pdfium.FPDFBitmap_GetFormat(raw)
        stride = pdfium.FPDFBitmap_GetStride(raw)
        
        if ex_buffer is None:
            needs_free = True
            total_bytes = stride * height
            first_item = pdfium.FPDFBitmap_GetBuffer(raw)
            if first_item.value is None:
                raise PdfiumError("Failed to get bitmap buffer (null pointer returned)")
            buffer_ptr = ctypes.cast(first_item, ctypes.POINTER(ctypes.c_ubyte * total_bytes))
            buffer = buffer_ptr.contents
        else:
            needs_free = False
            buffer = ex_buffer
        
        return cls(
            raw = raw,
            buffer = buffer,
            width = width,
            height = height,
            stride = stride,
            format = format,
            rev_byteorder = rev_byteorder,
            needs_free = needs_free,
        )
    
    
    @classmethod
    def new_native(cls, width, height, format, rev_byteorder=False):
        """
        Create a new bitmap using :func:`FPDFBitmap_CreateEx`, with a buffer allocated by Python/ctypes.
        Refer to :class:`.PdfBitmapInfo` for parameter documentation.
        
        Bitmaps created by this function are always packed (no unused bytes at line end).
        """
        
        stride = width * BitmapTypeToNChannels[format]
        total_bytes = stride * height
        buffer = (ctypes.c_ubyte * total_bytes)()
        raw = pdfium.FPDFBitmap_CreateEx(width, height, format, buffer, stride)
        
        # alternatively, we could call the constructor directly with the information from above
        return cls.from_raw(raw, rev_byteorder, buffer)
    
    
    @classmethod
    def new_foreign(cls, width, height, format, rev_byteorder=False, force_packed=False):
        """
        Create a new bitmap using :func:`FPDFBitmap_CreateEx`, with a buffer allocated by PDFium.
        
        Using this method is discouraged. Prefer :meth:`.new_native` instead.
        
        Parameters:
            force_packed (bool):
                Whether to force the creation of a packed bitmap, where ``stride == width * n_channels``. [#force-packed]_
                Otherwise, there may be a padding of unused bytes at line end.
        
        .. [#force-packed] Note that this is not officially approved by PDFium's documentation.
        """
        
        if force_packed:
            stride = width * BitmapTypeToNChannels[format]
        else:
            stride = 0
        
        raw = pdfium.FPDFBitmap_CreateEx(width, height, format, None, stride)
        return cls.from_raw(raw, rev_byteorder)
    
    
    @classmethod
    def new_foreign_simple(cls, width, height, use_alpha, rev_byteorder=False):
        """
        Create a new bitmap using :func:`FPDFBitmap_Create`. The buffer is allocated by PDFium.
        The resulting bitmap is supposed to be packed (i. e. no gap of unused bytes between lines).
        
        Using this method is discouraged. Prefer :meth:`.new_native` instead.
        
        Parameters:
            use_alpha (bool):
                Indicate whether the alpha channel is used.
                If True, the pixel format will be BGRA. Otherwise, it will be BGRX.
        """
        raw = pdfium.FPDFBitmap_Create(width, height, use_alpha)
        return cls.from_raw(raw, rev_byteorder)
    
    
    def fill_rect(self, left, top, width, height, color):
        """
        Fill a rectangle on the bitmap with the given color.
        The coordinate system starts at the top left corner of the image.
        
        Note:
            This function replaces the color values in the given rectangle. It does not perform alpha compositing.
        
        Parameters:
            color (typing.Tuple[int, int, int, int]):
                RGBA fill color (a tuple of 4 integers ranging from 0 to 255).
        """
        c_color = color_tohex(color, self.rev_byteorder)
        pdfium.FPDFBitmap_FillRect(self.raw, left, top, width, height, c_color)
    
    
    # Assumption: If the result is a view of the buffer, it holds a reference to said buffer (directly or indirectly), so that a possible finalizer is not called prematurely. This seems to hold true for numpy and PIL.
    
    def to_numpy(self):
        """
        *Requires* :mod:`numpy`.
        
        Convert the bitmap to a NumPy array.
        
        The array contains as many rows as the bitmap is high.
        Each row contains as many pixels as the bitmap is wide.
        The length of each pixel corresponds to the number of channels.
        
        The resulting array is supposed to share memory with the original bitmap buffer, so changes to the buffer should be reflected in the array, and vice versa.
        
        This converter takes :attr:`~.PdfBitmapInfo.stride` into account.
        
        Returns:
            numpy.ndarray: NumPy array representation of the bitmap.
        """
        
        # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray
        
        if numpy is None:
            raise RuntimeError("NumPy library needs to be installed for to_numpy() converter.")
        
        array = numpy.ndarray(
            # layout: row major
            shape = (self.height, self.width, self.n_channels),
            dtype = ctypes.c_ubyte,
            buffer = self.buffer,
            # number of bytes per item for each nesting level (outer->inner, i. e. row, pixel, value)
            strides = (self.stride, self.n_channels, 1),
        )
        
        return array
    
    
    def to_pil(self):
        """
        *Requires* :mod:`PIL`.
        
        Convert the bitmap to a PIL image, using :func:`PIL.Image.frombuffer`.
        
        For ``RGBA``, ``RGBX`` and ``L`` buffers, PIL is supposed to share memory with the original bitmap buffer, so changes to the buffer should be reflected in the image. Otherwise, PIL will make a copy of the data.
        
        This converter takes :attr:`~.PdfBitmapInfo.stride` into account.
        
        Returns:
            PIL.Image.Image: PIL image representation of the bitmap.
        """
        
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.frombuffer
        # https://pillow.readthedocs.io/en/stable/handbook/writing-your-own-image-plugin.html#the-raw-decoder
        
        if PIL is None:
            raise RuntimeError("Pillow library needs to be installed for to_pil() converter.")
        
        src_mode = self.mode
        dest_mode = BitmapTypeToStrReverse[self.format]
        
        image = PIL.Image.frombuffer(
            dest_mode,                  # target color format
            (self.width, self.height),  # size
            self.buffer,                # buffer
            "raw",                      # decoder
            src_mode,                   # input color format
            self.stride,                # bytes per line
            1,                          # orientation (top->bottom)
        )
        
        return image
