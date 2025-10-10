import io
import textwrap
from fpdf import FPDF


def text_to_pdf(text):
    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    margin_mm = 25
    pdf.set_margins(margin_mm, margin_mm, margin_mm)
    pdf.set_auto_page_break(auto=True, margin=margin_mm)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 7, text)

    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes
