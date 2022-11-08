# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

from pypdfium2._cli._parsers import (
    add_input_pdf,
    get_input_pdf,
)


def attach(parser):
    add_input_pdf(parser)
    parser.add_argument(
        "--max-depth",
        type = int,
        default = 15,
        help = "Maximum recursion depth to consider when parsing the table of contents",
    )


def main(args):
    pdf = get_input_pdf(args)
    toc = pdf.get_toc(
        max_depth = args.max_depth,
    )
    pdf.print_toc(toc)
