# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

# TODO import as namespace, rather than importing individual members
# TODO make publicly accessible without including individual members in the main namespace

import pypdfium2._pypdfium as pdfium


# NOTE FPDFBitmap_Unknown deliberately not handled

#: Get the number of channels for a PDFium bitmap format constant.
BitmapTypeToNChannels = {
    pdfium.FPDFBitmap_Gray: 1,
    pdfium.FPDFBitmap_BGR:  3,
    pdfium.FPDFBitmap_BGRA: 4,
    pdfium.FPDFBitmap_BGRx: 4,
}

#: Convert a PDFium bitmap format constant to string, assuming regular byte order.
BitmapTypeToStr = {
    pdfium.FPDFBitmap_Gray: "L",
    pdfium.FPDFBitmap_BGR:  "BGR",
    pdfium.FPDFBitmap_BGRA: "BGRA",
    pdfium.FPDFBitmap_BGRx: "BGRX",
}

#: Convert a PDFium bitmap format constant to string, assuming reversed byte order.
BitmapTypeToStrReverse = {
    pdfium.FPDFBitmap_Gray: "L",
    pdfium.FPDFBitmap_BGR:  "RGB",
    pdfium.FPDFBitmap_BGRA: "RGBA",
    pdfium.FPDFBitmap_BGRx: "RGBX",
}

#: Convert a PDFium color space constant to string.
ColorspaceToStr = {
    pdfium.FPDF_COLORSPACE_UNKNOWN:    "?",
    pdfium.FPDF_COLORSPACE_DEVICEGRAY: "DeviceGray",
    pdfium.FPDF_COLORSPACE_DEVICERGB:  "DeviceRGB",
    pdfium.FPDF_COLORSPACE_DEVICECMYK: "DeviceCMYK",
    pdfium.FPDF_COLORSPACE_CALGRAY:    "CalGray",
    pdfium.FPDF_COLORSPACE_CALRGB:     "CalRGB",
    pdfium.FPDF_COLORSPACE_LAB:        "Lab",
    pdfium.FPDF_COLORSPACE_ICCBASED:   "ICCBased",
    pdfium.FPDF_COLORSPACE_SEPARATION: "Separation",
    pdfium.FPDF_COLORSPACE_DEVICEN:    "DeviceN",
    pdfium.FPDF_COLORSPACE_INDEXED:    "Indexed",  # i. e. palettized
    pdfium.FPDF_COLORSPACE_PATTERN:    "Pattern",
}

#: Convert a PDFium view mode constant (:attr:`PDFDEST_VIEW_*`) to string.
ViewmodeToStr = {
    pdfium.PDFDEST_VIEW_UNKNOWN_MODE: "?",
    pdfium.PDFDEST_VIEW_XYZ:   "XYZ",
    pdfium.PDFDEST_VIEW_FIT:   "Fit",
    pdfium.PDFDEST_VIEW_FITH:  "FitH",
    pdfium.PDFDEST_VIEW_FITV:  "FitV",
    pdfium.PDFDEST_VIEW_FITR:  "FitR",
    pdfium.PDFDEST_VIEW_FITB:  "FitB",
    pdfium.PDFDEST_VIEW_FITBH: "FitBH",
    pdfium.PDFDEST_VIEW_FITBV: "FitBV",
}

#: Convert a PDFium error constant (:attr:`FPDF_ERR_*`) to string.
ErrorToStr = {
    pdfium.FPDF_ERR_SUCCESS:  "Success",
    pdfium.FPDF_ERR_UNKNOWN:  "Unknown error",
    pdfium.FPDF_ERR_FILE:     "File access error",
    pdfium.FPDF_ERR_FORMAT:   "Data format error",
    pdfium.FPDF_ERR_PASSWORD: "Incorrect password error",
    pdfium.FPDF_ERR_SECURITY: "Unsupported security scheme error",
    pdfium.FPDF_ERR_PAGE:     "Page not found or content error",
}

#: Convert a PDFium object type constant (:attr:`FPDF_PAGEOBJ_*`) to string.
ObjectTypeToStr = {
    pdfium.FPDF_PAGEOBJ_UNKNOWN: "?",
    pdfium.FPDF_PAGEOBJ_TEXT:    "text",
    pdfium.FPDF_PAGEOBJ_PATH:    "path",
    pdfium.FPDF_PAGEOBJ_IMAGE:   "image",
    pdfium.FPDF_PAGEOBJ_SHADING: "shading",
    pdfium.FPDF_PAGEOBJ_FORM:    "form",
}

#: Convert an object type string to a PDFium constant. Inversion of :data:`.ObjectTypeToStr`.
ObjectTypeToConst = {v: k for k, v in ObjectTypeToStr.items()}

#: Convert a rotation value in degrees to a PDFium constant.
RotationToConst = {
    0:   0,
    90:  1,
    180: 2,
    270: 3,
}

#: Convert a PDFium rotation constant to a value in degrees. Inversion of :data:`.RotationToConst`.
RotationToDegrees = {v: k for k, v in RotationToConst.items()}
