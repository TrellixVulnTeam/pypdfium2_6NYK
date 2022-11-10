# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

__all__ = ["PdfAttachment"]

import ctypes
import pypdfium2._pypdfium as pdfium
from pypdfium2._helpers.misc import PdfiumError


def _encode_key(key):
    if isinstance(key, str):
        return key.encode("utf-8")
    elif isinstance(key, bytes):
        return key
    else:
        raise TypeError("Key may be str or bytes, but %s was given." % type(key).__name__)


class PdfAttachment:
    """
    TODO
    """
    
    def __init__(self, raw, pdf):
        self.raw = raw
        self.pdf = pdf
    
    
    def get_name(self):
        """
        TODO
        """
        n_bytes = pdfium.FPDFAttachment_GetName(self.raw, None, 0)
        buffer = ctypes.create_string_buffer(n_bytes)
        buffer_ptr = ctypes.cast(buffer, ctypes.POINTER(pdfium.FPDF_WCHAR))
        pdfium.FPDFAttachment_GetName(self.raw, buffer_ptr, n_bytes)
        return buffer.raw[:n_bytes-2].decode("utf-16-le")
    
    
    def get_data(self):
        """
        TODO
        """
                
        n_bytes = ctypes.c_ulong()
        pdfium.FPDFAttachment_GetFile(self.raw, None, 0, n_bytes)
        n_bytes = n_bytes.value
        if n_bytes == 0:
            raise PdfiumError("Failed to extract attachment (buffer length %s)." % (n_bytes, ))
        
        buffer = (ctypes.c_ubyte * n_bytes)()
        out_buflen = ctypes.c_ulong()
        success = pdfium.FPDFAttachment_GetFile(self.raw, buffer, n_bytes, out_buflen)
        out_buflen = out_buflen.value
        if not success:
            raise PdfiumError("Failed to extract attachment (error status).")
        if n_bytes < out_buflen:
            raise PdfiumError("Failed to extract attachment (expected %s bytes, but got %s)." % (n_bytes, out_buflen))
        
        return buffer
    
    
    def set_data(self, data):
        """
        TODO
        """
        success = pdfium.FPDFAttachment_SetFile(self.raw, self.pdf.raw, data, len(data))
        if not success:
            raise PdfiumError("Failed to set attachment data.")
    
    
    def has_key(self, key):
        """
        TODO
        """
        return pdfium.FPDFAttachment_HasKey(self.raw, _encode_key(key))
    
    
    def get_value_type(self, key):
        """
        TODO
        """
        return pdfium.FPDFAttachment_GetValueType(self.raw, _encode_key(key))
    
    
    def get_str_value(self, key):
        """
        TODO
        """
        
        key = _encode_key(key)
        n_bytes = pdfium.FPDFAttachment_GetStringValue(self.raw, key, None, 0)
        if n_bytes == 2:
            raise PdfiumError("Failed to get value of key '%s' (type is not str or name)." % (key, ))
        if n_bytes <= 0:
            raise PdfiumError("Failed to get value of key '%s'." % (key, ))
        
        buffer = ctypes.create_string_buffer(n_bytes)
        buffer_ptr = ctypes.cast(buffer, ctypes.POINTER(pdfium.FPDF_WCHAR))
        pdfium.FPDFAttachment_GetStringValue(self.raw, key, buffer_ptr, n_bytes)
        
        return buffer.raw[:n_bytes-2].decode("utf-16-le")
    
    
    def set_str_value(self, key, value):
        """
        TODO
        """
        pass  # TODO
