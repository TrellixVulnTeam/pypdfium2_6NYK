# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

# NOTE ctypesgen bindings namespace is a kind of a mess, but we want the raw API to be part of our main namespace all the same
from pypdfium2._pypdfium import *
from pypdfium2._helpers import *
from pypdfium2.version import *
