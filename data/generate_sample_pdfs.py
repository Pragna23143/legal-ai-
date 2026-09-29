"""Generates sample PDF files for the legal agreements using ReportLab.

Outputs ready-to-test PDFs in data/samples/ directory.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data.sample_contracts import SAMPLE_CONTRACTS
from config import SAMPLES_DIR


def generate_pdf_for_contract(contract_data: dict, output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ContractTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        "ContractBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    )

    section_style = ParagraphStyle(
        "ContractSection",
        parent=styles["Heading2"],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4,
    )

    story = []

    # Title
    story.append(Paragraph(contract_data["title"], title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

    # Split lines
    lines = contract_data["text"].strip().split("\n")
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            story.append(Spacer(1, 6))
            continue

        if line_clean.startswith("SECTION ") or line_clean.isupper() and len(line_clean) < 70:
            story.append(Spacer(1, 8))
            story.append(Paragraph(line_clean, section_style))
        else:
            # Escape XML entities for ReportLab Paragraph
            escaped = (
                line_clean.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            story.append(Paragraph(escaped, body_style))

    doc.build(story)
    print(f"Generated PDF: {output_path}")


def generate_all_sample_pdfs():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    for sample in SAMPLE_CONTRACTS:
        filename = f"{sample['id']}.pdf"
        output_path = SAMPLES_DIR / filename
        generate_pdf_for_contract(sample, output_path)


if __name__ == "__main__":
    generate_all_sample_pdfs()
