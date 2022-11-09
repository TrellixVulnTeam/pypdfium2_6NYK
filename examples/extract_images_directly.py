#! /usr/bin/env python3
# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

import sys
import argparse
from pathlib import Path
from collections import namedtuple
import PIL.Image
import pypdfium2 as pdfium


def main():
    
    parser = get_parser()
    args = parser.parse_args()
    pdf = pdfium.PdfDocument(args.input)
    
    images = []
    for i, page in enumerate(pdf):
        batch = list( page.get_objects(filter=[pdfium.FPDF_PAGEOBJ_IMAGE]) )
        if len(batch) > 0:
            log("Page %s: found %s images" % (i+1, len(batch)))
            images += batch
    log("PDF: found %s images\n" % len(images))
    
    n_digits = len(str(len(images)))
    for i, image in enumerate(images):
        ex_gen = extract_smart(image, args.fallback_format, args.render_on_fallback)
        format = next(ex_gen)
        output_path = args.output_dir / ("%s_%0*d.%s" % (args.input.stem, n_digits, i+1, format))
        log(output_path)
        with open(output_path, "wb") as buffer:
            ex_gen.send(buffer)
        log()


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def get_parser():
    parser = argparse.ArgumentParser(
        description = "Try to extract images directly, fall back to bitmap re-encoding otherwise. While this should work in many common cases, it is possible that direct extraction produces wrong results on some documents.",
    )
    parser.add_argument(
        "input",
        type = Path,
        help = "Input PDF file",
    )
    parser.add_argument(
        "--output-dir", "-o",
        type = Path,
        help = "Output directory",
    )
    parser.add_argument(
        "--fallback-format", "-f",
        help = "Fallback image format to use if direct extraction fails.",
    )
    parser.add_argument(
        "--render-on-fallback", "-r",
        action = "store_true",
        help = "If the fallback code path is hit, whether the image should be rendered.",
    )
    return parser


def extract_smart(image_obj, fb_format=None, fb_render=False):
    
    pil_image = None
    data = None
    info = None
    
    try:
        data, info = extract_direct(image_obj)
    except ImageNotExtractableError as e:
        log(e)
        log("Falling back to bitmap-based extraction (may lead to loss of compression and/or quality)")
        pil_image = image_obj.get_bitmap(render=fb_render).to_pil()
    else:
        format = info.format
        if format == "raw":
            metadata = info.metadata
            pil_image = PIL.Image.frombuffer(
                info.mode,
                (metadata.width, metadata.height),
                image_obj.get_data(decode_simple=True),
                "raw", info.mode, 0, 1,
            )
        
    if pil_image:
        if fb_format:
            format = fb_format
        elif pil_image.mode == "CMYK":
            format = "tiff"
        else:
            format = "png"
    
    # let the caller send in a buffer after they were provided with the format
    buffer = yield format
    
    if pil_image:
        pil_image.save(buffer, format=format)
    else:
        buffer.write(data)
    
    # breakpoint preventing StopIteration on send()
    yield None


def extract_direct(image_obj):
    
    # An attempt at direct image extraction using PDFium
    # Limited in capabilities because PDFium's public API does not expose all the required information (see https://crbug.com/pdfium/1930 for considerations)
    
    # Currently, this function can...
    # - extract JPG and JPX images directly
    # - extract the raw pixel data if there are only simple filters
    
    all_filters = image_obj.get_filters()
    complex_filters = [f for f in all_filters if f not in pdfium.PdfImage.SIMPLE_FILTERS]
    metadata = image_obj.get_metadata()
    mode = get_pil_mode(metadata.colorspace, metadata.bits_per_pixel)
    
    log("All filters: %s" % all_filters)
    log("Complex filters: %s" % complex_filters)
    log("Mode: %s" % mode)
    log(pdfium.image_metadata_to_str(metadata))
    
    out_data = None
    out_format = None
    
    # TODO If there is only a single FlateDecode or LZWDecode filter, check if the raw data could be wrapped in a PNG or TIFF (to avoid decoding/re-encoding)
    
    if len(complex_filters) == 0:
        if mode:
            out_data = image_obj.get_data(decode_simple=True)
            out_format = "raw"
        else:
            raise ImageNotExtractableError("Unhandled color space: '%s' - don't know how to treat data" % pdfium.ColorspaceToStr[metadata.colorspace])
        
    elif len(complex_filters) == 1:
        f = complex_filters[0]
        if f == "DCTDecode":
            out_data = image_obj.get_data(decode_simple=True)
            out_format = "jpg"
        elif f == "JPXDecode":
            out_data = image_obj.get_data(decode_simple=True)
            out_format = "jp2"
        else:
            raise ImageNotExtractableError("Unhandled complex filter %s" % f)
        
        # Notes on other complex filters:
        # CCITTFaxDecode: In theory, could be extracted directly (with a TIFF header builder like pikepdf/models/_transcoding.py:generate_ccitt_header), but PDFium doesn't tell us which CCITT group encoding it is.
        # JBIG2Decode: PDF stores JBIG2 in special form. Header information is stripped, and global segments may be stored in a separate stream. In that form, the data would probably not be of much use, except perhaps for direct re-insertion into another PDF. We're not sure if it would be possible to re-combine this into a single JBIG2 file, or if any application could open this at all. PDFium doesn't provide us with the global segments, anyway.
        
    else:
        raise ImageNotExtractableError("Cannot handle multiple complex filters: %s" % (complex_filters, ))
    
    info = ImageInfo(out_format, mode, metadata, all_filters, complex_filters)
    return out_data, info


ImageInfo = namedtuple("ImageInfo", "format mode metadata all_filters complex_filters")

class ImageNotExtractableError (Exception):
    pass


def get_pil_mode(colorspace, bpp):
    # In theory, we could also handle indexed (palettized) and ICC-based color spaces, but PDFium currently does not provide access to the palette or the ICC profile
    if colorspace == pdfium.FPDF_COLORSPACE_DEVICEGRAY:
        if bpp == 1:
            return "1"
        else:
            return "L"
    elif colorspace == pdfium.FPDF_COLORSPACE_DEVICERGB:
        return "RGB"
    elif colorspace == pdfium.FPDF_COLORSPACE_DEVICECMYK:
        return "CMYK"
    else:
        return None


if __name__ == "__main__":
    main()
