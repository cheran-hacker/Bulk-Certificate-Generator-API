import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_pdf(
    recipient_name: str,
    certificate_title: str,
    event_name: str,
    organization_name: str,
    issue_date: str,
    certificate_code: str
) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setStrokeColor(colors.HexColor("#2c3e50"))
    c.setLineWidth(10)
    c.rect(30, 30, width - 60, height - 60)

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawCentredString(width / 2, height - 120, organization_name)

    c.setFont("Helvetica", 36)
    c.setFillColor(colors.HexColor("#e74c3c"))
    c.drawCentredString(width / 2, height - 200, certificate_title)

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#7f8c8d"))
    c.drawCentredString(width / 2, height - 260, "This is proudly presented to")

    c.setFont("Helvetica-Bold", 42)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 330, recipient_name)

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#7f8c8d"))
    c.drawCentredString(width / 2, height - 390, f"for successful participation in {event_name}")

    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(120, 100, f"Date: {issue_date}")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#95a5a6"))
    c.drawRightString(width - 120, 100, f"Certificate Code: {certificate_code}")

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
