
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated_certificates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_certificate(
    recipient_name: str,
    course_name: str,
    event_name: str,
    issue_date: str,
    recipient_id: str,
) -> str:
    """
    Generate one PDF certificate and return its file path.
    """
    output_path = OUTPUT_DIR / f"{recipient_id}.pdf"

    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(str(output_path), pagesize=(page_width, page_height))

    # Background
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Decorative border
    pdf.setStrokeColor(colors.HexColor("#1D4ED8"))
    pdf.setLineWidth(3)
    pdf.rect(12 * mm, 12 * mm, page_width - 24 * mm,
             page_height - 24 * mm, fill=0, stroke=1)

    # Certificate heading
    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 45 * mm,
        "CERTIFICATE OF ACHIEVEMENT",
    )

    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 65 * mm,
        "This certificate is proudly presented to",
    )

    # Recipient name
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 85 * mm,
        recipient_name,
    )

    # Course and event
    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 105 * mm,
        f"for completing {course_name}",
    )
    pdf.drawCentredString(
        page_width / 2,
        page_height - 115 * mm,
        f"at {event_name}",
    )

    # Issue date
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 135 * mm,
        f"Issue date: {issue_date}",
    )

    # Signature line
    pdf.setStrokeColor(colors.HexColor("#6B7280"))
    pdf.line(
        page_width / 2 - 35 * mm,
        30 * mm,
        page_width / 2 + 35 * mm,
        30 * mm,
    )
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(page_width / 2, 24 * mm, "Authorized Signature")

    pdf.save()

    return str(output_path)
