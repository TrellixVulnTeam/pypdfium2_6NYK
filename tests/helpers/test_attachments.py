# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

import ctypes
import pypdfium2 as pdfium
from ..conftest import TestFiles


def test_attachments():
    
    pdf = pdfium.PdfDocument(TestFiles.attachments)
    assert pdf.count_attachments() == 2
    
    attachment_a = pdf.get_attachment(0)
    assert attachment_a.get_name() == "1.txt"
    data_a = attachment_a.get_data()
    assert isinstance(data_a, (ctypes.c_ubyte * 4))
    assert str(data_a, encoding="utf-8") == "test"
    
    in_text = "pypdfium2 test"
    attachment_a.set_data(in_text.encode("utf-8"))
    assert str(attachment_a.get_data(), encoding="utf-8") == in_text
    
    attachment_b = pdf.get_attachment(1)
    assert attachment_b.get_name() == "attached.pdf"
    data_b = attachment_b.get_data()
    assert isinstance(data_b, (ctypes.c_ubyte * 5869))
    
    pdf_attached = pdfium.PdfDocument(data_b)
    assert len(pdf_attached) == 1
    page = pdf_attached[0]
    textpage = page.get_textpage()
    assert textpage.get_text_range() == "test"
    
    name_c = "Mona Lisa"
    attachment_c = pdf.add_attachment(name_c)
    assert attachment_c.get_name() == name_c
