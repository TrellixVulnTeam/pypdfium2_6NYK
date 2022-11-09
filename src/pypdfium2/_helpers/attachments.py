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
    
    
    def __contains__(self, key):
        return pdfium.FPDFAttachment_HasKey(self.raw, _encode_key(key))
    
    
    def __getitem__(self, key):
        
        key = _encode_key(key)
        if key not in self:
            raise KeyError("Attachment does not have key '%s'" % (key, ))
        
        type = self.get_value_type(key)
        if type == pdfium.FPDF_OBJECT_NULLOBJ:
            return None
        elif type in (pdfium.FPDF_OBJECT_STRING, pdfium.FPDF_OBJECT_NAME):
            pass  # TODO
        else:
            raise KeyError("Cannot extract key '%s' (unsupported value type '%s')" % (key, type))
    
    
    def __setitem__(self, key, value):
        pass  # TODO
    
    
    def get_value_type(self, key):
        """
        TODO
        """
        return pdfium.FPDFAttachment_GetValueType(self.raw, _encode_key(key))
    
    
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
