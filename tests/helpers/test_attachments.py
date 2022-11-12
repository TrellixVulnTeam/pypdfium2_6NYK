# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

import re
import ctypes
import pytest
import hashlib
import pypdfium2 as pdfium
from ..conftest import TestFiles, OutputDir


def test_attachments():
    
    pdf = pdfium.PdfDocument(TestFiles.attachments)
    assert pdf.count_attachments() == 2
    
    attachment_a = pdf.get_attachment(0)
    assert isinstance(attachment_a, pdfium.PdfAttachment)
    assert isinstance(attachment_a.raw, pdfium.FPDF_ATTACHMENT)
    assert attachment_a.get_name() == "1.txt"
    data_a = attachment_a.get_data()
    assert isinstance(data_a, (ctypes.c_char * 4))
    assert str(data_a, encoding="utf-8") == "test"
    
    assert attachment_a.has_key("CreationDate")
    assert attachment_a.get_str_value("CreationDate") == "D:20170712214438-07'00'"
    assert attachment_a.get_str_value("ModDate") == "D:20160115091400"
    
    exp_checksum = "098f6bcd4621d373cade4e832627b4f6"
    assert attachment_a.get_value_type("CheckSum") == pdfium.FPDF_OBJECT_STRING
    assert attachment_a.get_str_value("CheckSum") == "<%s>" % (exp_checksum.upper(), )
    assert exp_checksum == hashlib.md5(data_a).hexdigest()
    
    assert attachment_a.has_key("Size")
    assert attachment_a.get_value_type("Size") == pdfium.FPDF_OBJECT_NUMBER
    assert attachment_a.get_str_value("Size") == ""
    
    assert not attachment_a.has_key("asdf")
    assert attachment_a.get_str_value("asdf") == ""
    
    in_text = "pypdfium2 test"
    attachment_a.set_data(in_text.encode("utf-8"))
    assert str(attachment_a.get_data(), encoding="utf-8") == in_text
    
    attachment_b = pdf.get_attachment(1)
    assert attachment_b.get_name() == "attached.pdf"
    data_b = attachment_b.get_data()
    assert isinstance(data_b, (ctypes.c_char * 5869))
    
    pdf_attached = pdfium.PdfDocument(data_b)
    assert len(pdf_attached) == 1
    page = pdf_attached[0]
    textpage = page.get_textpage()
    assert textpage.get_text_range() == "test"
    
    name_c = "Mona Lisa.jpg"
    attachment_c = pdf.new_attachment(name_c)
    assert pdf.count_attachments() == 3
    assert attachment_c.get_name() == name_c
    
    with pytest.raises(pdfium.PdfiumError, match=re.escape("Failed to extract attachment (buffer length 0).")):
        attachment_c.get_data()
    
    with open(TestFiles.mona_lisa, "rb") as fh:
        data_c = fh.read()
    attachment_c.set_data(data_c)
    assert attachment_c.get_data().raw == data_c
    
    # NOTE new attachments may appear at an arbitrary index
    attachment_0 = pdf.get_attachment(0)
    assert attachment_0.get_name() == "1.txt"
    attachment_1 = pdf.get_attachment(1)
    assert attachment_1.get_name() == "Mona Lisa.jpg"
    attachment_2 = pdf.get_attachment(2)
    assert attachment_2.get_name() == "attached.pdf"
    
    pdf.del_attachment(2)
    assert pdf.count_attachments() == 2
    
    out_path = OutputDir / "attachments.pdf"
    with open(out_path, "wb") as buf:
        pdf.save(buf)
    
    pdf = pdfium.PdfDocument(out_path)
    assert pdf.count_attachments() == 2
    attachment_0 = pdf.get_attachment(0)
    assert attachment_0.get_name() == "1.txt"
    attachment_1 = pdf.get_attachment(1)
    assert attachment_1.get_name() == "Mona Lisa.jpg"
