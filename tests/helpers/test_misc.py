# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

import pytest
import pypdfium2 as pdfium
from pypdfium2 import pdf_consts

# TODO test auto_bitmap_format() and color_tohex()


@pytest.mark.parametrize(
    ["degrees", "const"],
    [
        (0,   0),
        (90,  1),
        (180, 2),
        (270, 3),
    ]
)
def test_rotation_conversion(degrees, const):
    assert pdf_consts.RotationToConst[degrees] == const
    assert pdf_consts.RotationToDegrees[const] == degrees


def _filter_namespace(prefix, skips, type=int):
    items = []
    for attr in dir(pdfium):
        value = getattr(pdfium, attr)
        if not attr.startswith(prefix) or not isinstance(value, type) or value in skips:
            continue
        items.append(value)
    return items


@pytest.mark.parametrize(
    ["mapping", "prefix", "skips"],
    [
        (pdf_consts.BitmapTypeToNChannels, "FPDFBitmap_", [pdfium.FPDFBitmap_Unknown]),
        (pdf_consts.BitmapTypeToStr, "FPDFBitmap_", [pdfium.FPDFBitmap_Unknown]),
        (pdf_consts.BitmapTypeToStrReverse, "FPDFBitmap_", [pdfium.FPDFBitmap_Unknown]),
        (pdf_consts.ColorspaceToStr, "FPDF_COLORSPACE_", []),
        (pdf_consts.ViewmodeToStr, "PDFDEST_VIEW_", []),
        (pdf_consts.ErrorToStr, "FPDF_ERR_", []),
        (pdf_consts.ObjectTypeToStr, "FPDF_PAGEOBJ_", []),
    ]
)
def test_const_converters(prefix, mapping, skips):
    items = _filter_namespace(prefix, skips)
    assert len(items) == len(mapping)
    for item in items:
        assert item in mapping
