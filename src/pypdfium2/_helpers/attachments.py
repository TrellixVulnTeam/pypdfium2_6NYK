# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

__all__ = ["PdfAttachment"]

import ctypes
import pypdfium2._pypdfium as pdfium


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
        buffer = ctypes.create_string_buffer(n_bytes+2)
        pdfium.FPDFAttachment_GetName(self.raw, buffer, n_bytes)
        return buffer.raw[:n_bytes].decode("utf-16-le")
    
    
    def get_data(self):
        """
        TODO
        """
        pass  # TODO
    
    
    def has_key(self, key):
        pass  # TODO
    
    
    def get_value_type(self, key):
        """
        TODO
        """
        return pdfium.FPDFAttachment_GetValueType(self.raw, _encode_key(key))
    
    
    def get_str_value(self, key):
        """
        TODO
        """
        pass  # TODO
    
    
    def set_str_value(self, key, value):
        """
        TODO
        """
        pass  # TODO
