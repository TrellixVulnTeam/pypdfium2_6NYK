# SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR BSD-3-Clause

__all__ = ["PdfPage", "PdfColorScheme"]

import math
import ctypes
import weakref
import logging
import pypdfium2._pypdfium as pdfium
from pypdfium2._helpers.misc import (
    RenderOptimizeMode,
    PdfiumError,
)
from pypdfium2._helpers.bitmap import PdfBitmap
from pypdfium2._helpers.textpage import PdfTextPage
from pypdfium2._helpers.pageobjects import PdfObject
from pypdfium2._helpers._internal import consts, utils

c_float = ctypes.c_float

logger = logging.getLogger(__name__)


class PdfPage:
    """
    Page helper class.
    
    Attributes:
        raw (FPDF_PAGE): The underlying PDFium page handle.
        pdf (PdfDocument): Reference to the document this page belongs to.
    """
    
    def __init__(self, raw, pdf):
        self.raw = raw
        self.pdf = pdf
        self._finalizer = weakref.finalize(
            self, self._static_close,
            self.raw, self.pdf,
        )
    
    def _tree_closed(self):
        if self.raw is None:
            return True
        return self.pdf._tree_closed()
    
    @staticmethod
    def _static_close(raw, parent):
        # logger.debug("Closing page")
        if parent._tree_closed():
            logger.critical("Document closed before page (this is illegal). Document: %s" % parent)
        pdfium.FPDF_ClosePage(raw)
    
    # TODO page labels
    
    def get_width(self):
        """
        Returns:
            float: Page width (horizontal size).
        """
        return pdfium.FPDF_GetPageWidthF(self.raw)
    
    def get_height(self):
        """
        Returns:
            float: Page height (vertical size).
        """
        return pdfium.FPDF_GetPageHeightF(self.raw)
    
    def get_size(self):
        """
        Returns:
            (float, float): Page width and height.
        """
        return (self.get_width(), self.get_height())
    
    def get_rotation(self):
        """
        Returns:
            int: Clockwise page rotation in degrees.
        """
        return consts.RotationToDegrees[ pdfium.FPDFPage_GetRotation(self.raw) ]
    
    def set_rotation(self, rotation):
        """ Define the absolute, clockwise page rotation (0, 90, 180, or 270 degrees). """
        pdfium.FPDFPage_SetRotation(self.raw, consts.RotationToConst[rotation])
    
    
    # pdfium's box getters currently do not inherit from parent nodes in the page tree (https://crbug.com/pdfium/1786)
    # the higher level page size and bounding box functions do, though
    
    def _get_box(self, box_func, fallback_func):
        left, bottom, right, top = c_float(), c_float(), c_float(), c_float()
        success = box_func(self.raw, left, bottom, right, top)
        if not success:
            return fallback_func()
        return (left.value, bottom.value, right.value, top.value)
    
    def _set_box(self, box_func, l, b, r, t):
        if not all(isinstance(val, (int, float)) for val in (l, b, r, t)):
            raise ValueError("Box values must be int or float.")
        box_func(self.raw, l, b, r, t)
    
    def get_mediabox(self):
        """
        Returns:
            (float, float, float, float):
            The page MediaBox in PDF canvas units, consisting of four coordinates (usually x0, y0, x1, y1).
            Falls back to ANSI A (0, 0, 612, 792) in case MediaBox is not defined.
        """
        return self._get_box(pdfium.FPDFPage_GetMediaBox, lambda: (0, 0, 612, 792))
    
    def set_mediabox(self, l, b, r, t):
        """
        Set the page's MediaBox by passing four :class:`float` coordinates (usually x0, y0, x1, y1).
        """
        self._set_box(pdfium.FPDFPage_SetMediaBox, l, b, r, t)
    
    def get_cropbox(self):
        """
        Returns:
            The page's CropBox (If not defined, falls back to MediaBox).
        """
        return self._get_box(pdfium.FPDFPage_GetCropBox, self.get_mediabox)
    
    def set_cropbox(self, l, b, r, t):
        """
        Set the page's CropBox.
        """
        self._set_box(pdfium.FPDFPage_SetCropBox, l, b, r, t)
    
    def get_bleedbox(self):
        """
        Returns:
            The page's BleedBox (If not defined, falls back to CropBox).
        """
        return self._get_box(pdfium.FPDFPage_GetBleedBox, self.get_cropbox)
    
    def set_bleedbox(self, l, b, r, t):
        """
        Set the page's BleedBox.
        """
        self._set_box(pdfium.FPDFPage_SetBleedBox, l, b, r, t)
    
    def get_trimbox(self):
        """
        Returns:
            The page's TrimBox (If not defined, falls back to CropBox).
        """
        return self._get_box(pdfium.FPDFPage_GetTrimBox, self.get_cropbox)
    
    def set_trimbox(self, l, b, r, t):
        """
        Set the page's TrimBox.
        """
        self._set_box(pdfium.FPDFPage_SetTrimBox, l, b, r, t)
    
    def get_artbox(self):
        """
        Returns:
            The page's ArtBox (If not defined, falls back to CropBox).
        """
        return self._get_box(pdfium.FPDFPage_GetArtBox, self.get_cropbox)
    
    def set_artbox(self, l, b, r, t):
        """
        Set the page's ArtBox.
        """
        self._set_box(pdfium.FPDFPage_SetArtBox, l, b, r, t)
    
    
    def get_bbox(self):
        """
        TODO docs
        """
        # TODO test integration
        rect = pdfium.FS_RECTF()
        success = pdfium.FPDF_GetPageBoundingBox(self.raw, rect)
        if not success:
            raise PdfiumError("Failed to get page bounding box.")
        return (rect.left, rect.bottom, rect.right, rect.top)
    
    
    def get_textpage(self):
        """
        Returns:
            PdfTextPage: The text page that corresponds to this page.
        """
        textpage = pdfium.FPDFText_LoadPage(self.raw)
        if not textpage:
            raise PdfiumError("Failed to load text page.")
        return PdfTextPage(textpage, self)
    
    
    def insert_object(self, pageobj):
        """
        Insert a page object into the page.
        
        The page object must not belong to a page yet. If it belongs to a PDF, this page must be part of the PDF.
        
        Position and form are defined by the object's matrix.
        If it is the identity matrix, the object will appear as-is on the bottom left corner of the page.
        
        Parameters:
            pageobj (PdfObject): The page object to insert.
        """
        
        if pageobj.page:
            raise ValueError("The pageobject you attempted to insert already belongs to a page.")
        if pageobj.pdf and (pageobj.pdf is not self.pdf):
            raise ValueError("The pageobject you attempted to insert belongs to a different PDF.")
        
        pdfium.FPDFPage_InsertObject(self.raw, pageobj.raw)
        pageobj._detach_finalizer()
        pageobj.page = self
        pageobj.pdf = self.pdf
    
    
    def remove_object(self, pageobj):
        """
        Remove a page object from the page. The page object must not be used afterwards.
        
        Parameters:
            pageobj (PdfObject): The page object to remove.
        """
        
        # TODO testing
        
        if pageobj.page is not self:
            raise ValueError("The page object you attempted to remove is not part of this page.")
        
        pdfium.FPDFPage_RemoveObject(self.raw, pageobj.raw)
        pageobj._attach_finalizer()
        pageobj.page = None
    
    
    def generate_content(self):
        """
        Generate page content to apply additions, removals or modifications of page objects.
        
        If page content was changed, this function should be called once before saving the document or re-loading the page.
        """
        success = pdfium.FPDFPage_GenerateContent(self.raw)
        if not success:
            raise PdfiumError("Failed to generate page content.")
    
    
    def get_objects(self, filter=None, max_depth=2, form=None, level=0):
        """
        Iterate through the page objects on this page.
        
        Parameters:
            filter (typing.Sequence[int] | None):
                TODO
            max_depth (int):
                Maximum recursion depth to consider when descending into Form XObjects.
        
        Yields:
            :class:`.PdfObject`: The page object.
        """
        
        if form is None:
            count_objects = pdfium.FPDFPage_CountObjects
            get_object = pdfium.FPDFPage_GetObject
            parent = self.raw
        else:
            count_objects = pdfium.FPDFFormObj_CountObjects
            get_object = pdfium.FPDFFormObj_GetObject
            parent = form
        
        n_objects = count_objects(parent)
        if n_objects == 0:
            return
        elif n_objects < 0:
            raise PdfiumError("Failed to get number of page objects.")
        
        for i in range(n_objects):
            
            raw_obj = get_object(parent, i)
            if raw_obj is None:
                raise PdfiumError("Failed to get page object.")
            
            helper_obj = PdfObject(
                raw = raw_obj,
                page = self,
                pdf = self.pdf,
                level = level,
            )
            if not filter or helper_obj.type in filter:
                yield helper_obj
            
            if helper_obj.type == pdfium.FPDF_PAGEOBJ_FORM and level < max_depth-1:
                yield from self.get_objects(
                    filter = filter,
                    max_depth = max_depth,
                    form = raw_obj,
                    level = level + 1,
                )
    
    
    def flatten(self, flag=pdfium.FLAT_NORMALDISPLAY):
        """
        TODO
        """
        # NOTE Highly unreliable as of pdfium 5406 (takes no effect but still returns success in many cases)
        rc = pdfium.FPDFPage_Flatten(self.raw, flag)
        if rc == pdfium.FLATTEN_FAIL:
            raise PdfiumError("Failed to flatten annotations / form fileds.")
        return rc
    
    
    def render_matrix(
            self,
            size,
            matrix,
            clipping,
            bitmap_maker = PdfBitmap.new_native,
            fill_color = (255, 255, 255, 255),
            **kwargs
        ):
        """
        TODO
        """
        
        # work in progress
        
        cl_format, rev_byteorder, flags = _parse_renderopts(
            fill_color = fill_color,
            color_scheme = None,
            **kwargs
        )
        width, height = size
        
        bitmap = bitmap_maker(
            width = width,
            height = height,
            format = cl_format,
            rev_byteorder = rev_byteorder,
        )
        bitmap.fill_rect(0, 0, width, height, fill_color)
        
        pdfium.FPDF_RenderPageBitmapWithMatrix(bitmap.raw, self.raw, matrix.to_pdfium(), pdfium.FS_RECTF(*clipping), flags)
        
        return bitmap
    
    
    def render(
            self,
            scale = 1,
            rotation = 0,
            crop = (0, 0, 0, 0),
            fill_color = (255, 255, 255, 255),
            color_scheme = None,
            draw_forms = True,
            bitmap_maker = PdfBitmap.new_native,
            **kwargs
        ):
        """
        TODO
        """
        
        src_width  = math.ceil(self.get_width()  * scale)
        src_height = math.ceil(self.get_height() * scale)
        if rotation in (90, 270):
            src_width, src_height = src_height, src_width
        
        crop = [math.ceil(c*scale) for c in crop]
        width  = src_width  - crop[0] - crop[2]
        height = src_height - crop[1] - crop[3]
        if any(d < 1 for d in (width, height)):
            raise ValueError("Crop exceeds page dimensions")
        
        cl_format, rev_byteorder, flags = _parse_renderopts(
            fill_color = fill_color,
            color_scheme = color_scheme,
            **kwargs
        )
        
        bitmap = bitmap_maker(
            width = width,
            height = height,
            format = cl_format,
            rev_byteorder = rev_byteorder,
        )
        bitmap.fill_rect(0, 0, width, height, fill_color)
        
        render_args = (bitmap.raw, self.raw, -crop[0], -crop[3], src_width, src_height, consts.RotationToConst[rotation], flags)
        
        if color_scheme is None:
            pdfium.FPDF_RenderPageBitmap(*render_args)
        else:
            # TODO move pause struct creation to shared function
            ifsdk_pause = pdfium.IFSDK_PAUSE()
            ifsdk_pause.version = 1
            ifsdk_pause.NeedToPauseNow = utils.get_functype(pdfium.IFSDK_PAUSE, "NeedToPauseNow")(lambda _: False)
            
            fpdf_cs = color_scheme.convert(rev_byteorder)
            status = pdfium.FPDF_RenderPageBitmapWithColorScheme_Start(*render_args, fpdf_cs, ifsdk_pause)
            
            assert status == pdfium.FPDF_RENDER_DONE
            pdfium.FPDF_RenderPage_Close(self.raw)
        
        if draw_forms and (self.pdf.get_formtype() != pdfium.FORMTYPE_NONE):
            # TODO do something about FORM_OnAfterLoadPage() / FORM_OnBeforeClosePage()
            exit_formenv = (self.pdf._form_env is None)
            formenv = self.pdf.init_formenv()
            pdfium.FPDF_FFLDraw(formenv, *render_args)
            if exit_formenv:
                self.pdf.exit_formenv()
        
        return bitmap


def _auto_bitmap_format(fill_color, greyscale, prefer_bgrx):
    # no need to take alpha values of color_scheme into account (drawings are additive)
    if (fill_color[3] < 255):
        return pdfium.FPDFBitmap_BGRA
    elif greyscale:
        return pdfium.FPDFBitmap_Gray
    elif prefer_bgrx:
        return pdfium.FPDFBitmap_BGRx
    else:
        return pdfium.FPDFBitmap_BGR


def _parse_renderopts(
        fill_color,
        color_scheme,
        greyscale = False,
        optimize_mode = None,
        draw_annots = True,
        no_smoothtext = False,
        no_smoothimage = False,
        no_smoothpath = False,
        force_halftone = False,
        limit_image_cache = False,
        rev_byteorder = False,
        prefer_bgrx = False,
        force_bitmap_format = None,
        extra_flags = 0,
    ):
    
    if force_bitmap_format is None:
        cl_format = _auto_bitmap_format(fill_color, greyscale, prefer_bgrx)
    else:
        cl_format = force_bitmap_format
    
    if cl_format == pdfium.FPDFBitmap_Gray:
        rev_byteorder = False
    
    flags = extra_flags
    if greyscale:
        flags |= pdfium.FPDF_GRAYSCALE
    if draw_annots:
        flags |= pdfium.FPDF_ANNOT
    if no_smoothtext:
        flags |= pdfium.FPDF_RENDER_NO_SMOOTHTEXT
    if no_smoothimage:
        flags |= pdfium.FPDF_RENDER_NO_SMOOTHIMAGE
    if no_smoothpath:
        flags |= pdfium.FPDF_RENDER_NO_SMOOTHPATH
    if force_halftone:
        flags |= pdfium.FPDF_RENDER_FORCEHALFTONE
    if limit_image_cache:
        flags |= pdfium.FPDF_RENDER_LIMITEDIMAGECACHE
    if rev_byteorder:
        flags |= pdfium.FPDF_REVERSE_BYTE_ORDER
    if color_scheme and color_scheme.fill_to_stroke:
        flags |= pdfium.FPDF_CONVERT_FILL_TO_STROKE
    
    if optimize_mode is RenderOptimizeMode.LCD_DISPLAY:
        flags |= pdfium.FPDF_LCD_TEXT
    elif optimize_mode is RenderOptimizeMode.PRINTING:
        flags |= pdfium.FPDF_PRINTING
    elif optimize_mode:
        raise ValueError("Invalid optimize_mode %s" % optimize_mode)
    
    return cl_format, rev_byteorder, flags


class PdfColorScheme:
    """
    Rendering color scheme.
    Each color shall be provided as a list of values for red, green, blue and alpha, ranging from 0 to 255.
    """
    
    def __init__(
            self,
            path_fill,
            path_stroke,
            text_fill,
            text_stroke,
            fill_to_stroke = False,
        ):
        self.colors = dict(
            path_fill_color = path_fill,
            path_stroke_color = path_stroke,
            text_fill_color = text_fill,
            text_stroke_color = text_stroke,
        )
        self.fill_to_stroke = fill_to_stroke
    
    def convert(self, rev_byteorder):
        """
        Returns:
            The color scheme as :class:`FPDF_COLORSCHEME` object.
        """
        fpdf_cs = pdfium.FPDF_COLORSCHEME()
        for key, value in self.colors.items():
            setattr(fpdf_cs, key, utils.color_tohex(value, rev_byteorder))
        return fpdf_cs
