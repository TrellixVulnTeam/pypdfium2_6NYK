# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

from pathlib import Path
import pypdfium2._namespace as pdfium
from pypdfium2._cli._parsers import (
    add_input,
    get_input,
)


def attach(parser):
    add_input(parser)
    parser.add_argument(
        "--output-dir", "-o",
        required = True,
        type = Path,
        help = "Output directory to take the extracted images",
    )
    parser.add_argument(
        "--format",
        default = "jpg",
        help = "Image format to use when saving the bitmaps",
    )
    parser.add_argument(
        "--render",
        action = "store_true",
        help = "Whether to get rendered bitmaps, taking masks and transform matrices into account.",
    )
    parser.add_argument(
        "--max-depth",
        type = int,
        default = 2,
        help = "Maximum recursion depth to consider when looking for page objects.",
    )


def main(args):
    
    if not args.output_dir.is_dir():
        raise NotADirectoryError(args.output_dir)
    
    pdf = get_input(args)
    
    image_objs = []
    for i in args.pages:
        page = pdf.get_page(i)
        obj_searcher = page.get_objects(
            filter = (pdfium.FPDF_PAGEOBJ_IMAGE, ),
            max_depth = args.max_depth,
        )
        image_objs += list(obj_searcher)
    
    n_digits = len(str(len(image_objs)))
    for i, obj in enumerate(image_objs):
        pil_image = obj.get_bitmap(render=args.render).to_pil()
        output_path = args.output_dir / ("%s_%0*d.%s" % (args.input.stem, n_digits, i+1, args.format))
        pil_image.save(output_path)
