from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas


def generate_asset_management_report(
    output_path: Path,
    report_title: str,
    report_description: str,
    total_assets_label: str,
    total_assets: int,
    assets_label: str,
    reference_label: str,
    status_label: str,
    tags_label: str,
    completed_status: str,
    assets: list[dict[str, str]],
) -> Path:
    """
    Génère un rapport PDF avec des textes traduits
    et des données dynamiques venant de la DB.
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

    # Titre
    pdf.setFont("Helvetica-Bold", 18)

    pdf.drawString(
        72,
        page_height - 72,
        report_title,
    )

    # Description
    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        72,
        page_height - 115,
        report_description,
    )

    # Total assets
    pdf.drawString(
        72,
        page_height - 145,
        f"{total_assets_label}: {total_assets}",
    )

    # Status général du rapport
    pdf.drawString(
        72,
        page_height - 175,
        f"{status_label}: {completed_status}",
    )

    # Position à partir de laquelle
    # on commence à afficher les assets
    y_position = page_height - 220

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        72,
        y_position,
        assets_label,
    )

    y_position -= 30

    # Afficher chaque asset
    for asset in assets:
        pdf.setFont("Helvetica-Bold", 12)

        pdf.drawString(
            80,
            y_position,
            asset["name"],
        )

        y_position -= 20

        pdf.setFont("Helvetica", 11)

        pdf.drawString(
            90,
            y_position,
            f'{reference_label}: {asset["reference"]}',
        )

        y_position -= 20

        pdf.drawString(
            90,
            y_position,
            f'{status_label}: {asset["status"]}',
        )

        y_position -= 20

        pdf.drawString(
            90,
            y_position,
            f'{tags_label}: {asset["tags"]}',
        )

        y_position -= 30

    # On sauvegarde seulement APRÈS
    # avoir terminé tout le contenu
    pdf.showPage()
    pdf.save()

    return output_path