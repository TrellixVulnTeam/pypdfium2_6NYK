# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

from ..conftest import TestFiles
import pypdfium2 as pdfium


def test_attachments():
    
    pdf = pdfium.PdfDocument(TestFiles.attachments)
    assert pdf.count_attachments() == 2
    
    attachment_a = pdf.get_attachment(0)
    assert attachment_a.get_name() == "1.txt"
    
    attachment_b = pdf.get_attachment(1)
    assert attachment_b.get_name() == "attached.pdf"
