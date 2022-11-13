import math
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("render.pdf")
page = pdf[0]

page_w, page_h = page.get_size()

matrix = pdfium.PdfMatrix()

l, b, r, t = matrix.on_rect(
    0, 0, page_w, page_h,
)
w = math.ceil(r - l)
h = math.ceil(t - b)
print(l, b, r, t, w, h)

clipping = (
    150,  # left
    150,  # top
    w - 150,  # right
    h - 250,  # bottom
)

bitmap = page.render_matrix((w, h), matrix, clipping)
bitmap.to_pil().show()
