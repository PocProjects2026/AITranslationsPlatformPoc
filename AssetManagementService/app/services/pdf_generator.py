from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


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
    Generate an Asset Management PDF report.

    Static labels are already translated before reaching
    this function.

    Dynamic asset data comes from the database.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=report_title,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )

    description_style = ParagraphStyle(
        "ReportDescription",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#555555"),
        spaceAfter=7 * mm,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=5 * mm,
        spaceAfter=4 * mm,
    )

    normal_style = ParagraphStyle(
        "TableText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
    )

    header_style = ParagraphStyle(
        "TableHeader",
        parent=normal_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story = []

    # --------------------------------------------------
    # Report header
    # --------------------------------------------------

    story.append(
        Paragraph(
            report_title,
            title_style,
        )
    )

    story.append(
        Paragraph(
            report_description,
            description_style,
        )
    )

    # --------------------------------------------------
    # Report summary
    # --------------------------------------------------

    summary_data = [
        [
            Paragraph(
                f"<b>{total_assets_label}</b>",
                normal_style,
            ),
            Paragraph(
                str(total_assets),
                normal_style,
            ),
        ],
        [
            Paragraph(
                f"<b>{status_label}</b>",
                normal_style,
            ),
            Paragraph(
                completed_status,
                normal_style,
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            55 * mm,
            105 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F5F7FA"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(summary_table)

    story.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    # --------------------------------------------------
    # Assets section
    # --------------------------------------------------

    story.append(
        Paragraph(
            assets_label,
            section_style,
        )
    )

    table_data = [
        [
            Paragraph(
                assets_label,
                header_style,
            ),
            Paragraph(
                reference_label,
                header_style,
            ),
            Paragraph(
                status_label,
                header_style,
            ),
            Paragraph(
                tags_label,
                header_style,
            ),
        ]
    ]

    for asset in assets:
        table_data.append(
            [
                Paragraph(
                    asset["name"],
                    normal_style,
                ),
                Paragraph(
                    asset["reference"],
                    normal_style,
                ),
                Paragraph(
                    asset["status"],
                    normal_style,
                ),
                Paragraph(
                    asset["tags"] or "-",
                    normal_style,
                ),
            ]
        )

    assets_table = Table(
        table_data,
        colWidths=[
            45 * mm,
            38 * mm,
            32 * mm,
            45 * mm,
        ],
        repeatRows=1,
    )

    assets_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#27364B"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F8FAFC"),
                    ],
                ),
            ]
        )
    )

    story.append(assets_table)

    document.build(
        story,
        onFirstPage=_add_page_footer,
        onLaterPages=_add_page_footer,
    )

    return output_path


def _add_page_footer(canvas, document) -> None:
    """
    Add a page number to every PDF page.
    """

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        8,
    )

    canvas.setFillColor(
        colors.HexColor("#777777")
    )

    canvas.drawCentredString(
        A4[0] / 2,
        10 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()