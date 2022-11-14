.. SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
.. SPDX-License-Identifier: CC-BY-4.0

Python API
==========

.. warning::
    PDFium is not thread-compatible. If you need to parallelise time-consuming PDFium tasks, use processes instead of threads.

.. TODO add some note about object finalization / memory management


Version
*******
.. automodule:: pypdfium2.version

Document
********
.. automodule:: pypdfium2._helpers.document

Page
****
.. automodule:: pypdfium2._helpers.page

Page Objects
************
.. automodule:: pypdfium2._helpers.pageobjects
   :show-inheritance:

Text Page
*********
.. automodule:: pypdfium2._helpers.textpage

Bitmap
******
.. automodule:: pypdfium2._helpers.bitmap

Matrix
******
.. automodule:: pypdfium2._helpers.matrix

Attachment
**********
.. automodule:: pypdfium2._helpers.attachment

Miscellaneous
*************
.. automodule:: pypdfium2._helpers.misc
