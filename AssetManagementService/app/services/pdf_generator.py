from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas


def generate_sample_pdf(
    output_path: Path,
    report_title: str,
    report_description: str,
    total_assets_label: str,
    total_assets: int,
    status_label: str,
    completed_status: str,
) -> Path:
    """
    Génère un rapport PDF avec des textes traduits
    et des données dynamiques.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf = Canvas(
        str(output_path),
        pagesize=A4,
    )

    _, page_height = A4

    pdf.setTitle(report_title)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(
        72,
        page_height - 72,
        report_title,
    )

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        72,
        page_height - 115,
        report_description,
    )

    pdf.drawString(
        72,
        page_height - 145,
        f"{total_assets_label}: {total_assets}",
    )

    pdf.drawString(
        72,
        page_height - 175,
        f"{status_label}: {completed_status}",
    )

    pdf.showPage()
    pdf.save()

    return output_path