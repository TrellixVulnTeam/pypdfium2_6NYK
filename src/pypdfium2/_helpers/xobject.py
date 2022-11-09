# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

__all__ = ["PdfXObject"]

import weakref
import logging
import pypdfium2._pypdfium as pdfium
from pypdfium2._helpers.pageobjects import PdfObject

logger = logging.getLogger(__name__)


class PdfXObject:
    """
    XObject helper class.
    
    Attributes:
        raw (FPDF_XOBJECT): The underlying PDFium XObject handle.
        pdf (PdfDocument): Reference to the document this XObject belongs to.
    """
    
    def __init__(self, raw, pdf):
        self.raw = raw
        self.pdf = pdf
        self._finalizer = weakref.finalize(
            self, self._static_close,
            self.raw, self.pdf,
        )
    
    
    def _tree_closed(self):
        if self.raw is None:
            return True
        return self.pdf._tree_closed()
    
    @staticmethod
    def _static_close(raw, parent):
        # logger.debug("Closing XObject")
        if parent._tree_closed():
            logger.critical("Document closed before XObject (this is illegal). Document: %s" % parent)
        pdfium.FPDF_CloseXObject(raw)
    
    
    def as_pageobject(self):
        """
        Returns:
            PdfObject: An independent page object representation of the XObject.
            If multiple page objects are created from one XObject, they share resources.
            Page objects created from an XObject remain valid after the XObject is finalized.
        """
        raw_pageobj = pdfium.FPDF_NewFormObjectFromXObject(self.raw)
        return PdfObject(
            raw = raw_pageobj,
            pdf = self.pdf,
        )
