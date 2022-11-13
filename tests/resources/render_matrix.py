import math
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("render.pdf")
page = pdf[0]

matrix = pdfium.PdfMatrix()
width = math.ceil(page.get_width())
height = math.ceil(page.get_height())
bitmap = page.render_matrix((width, height), matrix, (0, 0, width, height))
bitmap.to_pil().show()
