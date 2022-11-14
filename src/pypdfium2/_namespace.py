# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

# NOTE the ctypesgen bindings namespace is kind of a mess, but we want the raw API to be part of our main namespace all the same

from pypdfium2._pypdfium import *
from pypdfium2.version import *
from pypdfium2._helpers import *
import pypdfium2._helpers._internal.consts as pdf_consts
