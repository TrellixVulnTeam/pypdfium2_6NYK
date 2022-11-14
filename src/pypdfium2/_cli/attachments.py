# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

from pathlib import Path
from pypdfium2._cli._parsers import (
    add_input, get_input,
    parse_numtext,
)

ACTION_LIST = "list"
ACTION_EXTRACT = "extract"
ACTION_EDIT = "edit"


# hook
def attach(parser):
    add_input(parser, pages=False)
    subparsers = parser.add_subparsers(dest="action")
    parser_list = subparsers.add_parser(
        ACTION_LIST,
    )
    parser_extract = subparsers.add_parser(
        ACTION_EXTRACT,
    )
    parser_extract.add_argument(
        "--numbers",
        type = parse_numtext,
    )
    parser_extract.add_argument(
        "--output-dir", "-o",
        type = Path,
        required = True,
    )
    parser_edit = subparsers.add_parser(
        ACTION_EDIT,
    )


def main(args):
    
    pdf = get_input(args)
    n_attachments = pdf.count_attachments()
    
    if args.action == ACTION_LIST:
        for i in range(n_attachments):
            attachment = pdf.get_attachment(i)
            print("[%s]" % (i+1, ), attachment.get_name())
    
    elif args.action == ACTION_EXTRACT:
        
        if not args.numbers:
            args.numbers = range(n_attachments)
        n_digits = len(str( max(args.numbers) + 1 ))
        
        for i in args.numbers:
            attachment = pdf.get_attachment(i)
            name = attachment.get_name()
            out_path = args.output_dir / ("%0*d_%s" % (n_digits, i+1, name))
            out_path.write_bytes( attachment.get_data() )
    
    elif args.action == ACTION_EDIT:
        pass
