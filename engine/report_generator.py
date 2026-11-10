"""
report_generator.py
Modul pembuatan laporan audit kepatuhan regulasi berformat PDF formal
menggunakan ReportLab untuk kebutuhan eksekutif dan auditor Bank Mandiri.
"""

import io
from datetime import datetime
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_compliance_pdf_report(
    doc_info: Dict[str, Any],
    benchmark_info: Dict[str, Any],
    clauses: List[Dict[str, Any]],
    metrics: Dict[str, Any],
) -> bytes:
    """
    Menghasilkan dokumen PDF laporan audit keselarasan regulasi formal perbankan.
    Mengembalikan bytes PDF dalam memori untuk diunduh langsung.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#003d79"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#003d79"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    elements = []

    # 1. Header Institusional Laporan
    elements.append(Paragraph("PT BANK MANDIRI (PERSERO) TBK", ParagraphStyle("OrgName", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#003d79"), leading=11)))
    elements.append(Paragraph("LAPORAN AUDIT KESELARASAN REGULASI OPERASIONAL", title_style))
    elements.append(Paragraph("Evaluasi Kepatuhan Petunjuk Pelaksanaan Internal terhadap Ketentuan Regulator (POJK, BI, UU PDP)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003d79"), spaceBefore=2, spaceAfter=10))

    # 2. Metadata Audit
    audit_date = datetime.now().strftime("%d %B %Y")
    meta_data = [
        [
            Paragraph("<b>Dokumen yang Dievaluasi:</b>", body_style),
            Paragraph(f"{doc_info.get('title', '-')} ({doc_info.get('version', '')})", body_style),
            Paragraph("<b>Tanggal Audit:</b>", body_style),
            Paragraph(audit_date, body_style),
        ],
        [
            Paragraph("<b>Perihal / Pokok Bahasan:</b>", body_style),
            Paragraph(doc_info.get("subject", "-"), body_style),
            Paragraph("<b>Klasifikasi Kerahasiaan:</b>", body_style),
            Paragraph("Internal Bank Mandiri", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[120, 200, 100, 100])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # 3. Ringkasan Eksekutif (KPI Matriks Kepatuhan)
    elements.append(Paragraph("1. Ringkasan Tingkat Kepatuhan Regulasi", section_title_style))
    kpi_data = [
        [
            Paragraph("Indikator Audit", table_header_style),
            Paragraph("Jumlah Klausul", table_header_style),
            Paragraph("Persentase Dokumen", table_header_style),
            Paragraph("Status Tindak Lanjut", table_header_style),
        ],
        [
            Paragraph("Selaras (Memenuhi Ketentuan Regulator)", body_style),
            Paragraph(str(metrics["selaras"]["count"]), body_bold),
            Paragraph(f"{metrics['selaras']['pct']}%", body_style),
            Paragraph("Sesuai standar minimum regulator", body_style),
        ],
        [
            Paragraph("Tidak Selaras (Deviasi Regulasi / Risiko Sanksi)", body_bold),
            Paragraph(str(metrics["tidak_selaras"]["count"]), ParagraphStyle("RedText", parent=body_bold, textColor=colors.HexColor("#991b1b"))),
            Paragraph(f"{metrics['tidak_selaras']['pct']}%", ParagraphStyle("RedText2", parent=body_style, textColor=colors.HexColor("#991b1b"))),
            Paragraph("Wajib dilakukan revisi redaksional segera", ParagraphStyle("RedText3", parent=body_style, textColor=colors.HexColor("#991b1b"))),
        ],
        [
            Paragraph("Netral (Ketentuan Teknis Operasional Internal)", body_style),
            Paragraph(str(metrics["netral"]["count"]), body_bold),
            Paragraph(f"{metrics['netral']['pct']}%", body_style),
            Paragraph("Dapat dipertahankan tanpa perubahan", body_style),
        ],
        [
            Paragraph("Total Klausul Dianalisis", body_bold),
            Paragraph(str(metrics["total"]), body_bold),
            Paragraph("100.0%", body_bold),
            Paragraph("Audit Tahap 1 Selesai", body_bold),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[180, 80, 100, 160])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003d79")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#fef2f2")),  # Highlight merah baris tidak selaras
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#f1f5f9")),  # Total baris
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 14))

    # 4. Tabel Rincian Temuan Kepatuhan & Rekomendasi
    elements.append(Paragraph("2. Rincian Temuan Keselarasan Klausul (Gap Analysis Matrix)", section_title_style))

    findings_data = [
        [
            Paragraph("ID & Pasal Internal", table_header_style),
            Paragraph("Regulasi Acuan", table_header_style),
            Paragraph("Status", table_header_style),
            Paragraph("Pertimbangan Hukum (Reasoning)", table_header_style),
            Paragraph("Rekomendasi Tindakan", table_header_style),
        ]
    ]

    for c in clauses:
        status = c.get("status", "Netral")
        status_color = "#166534" if status == "Selaras" else ("#991b1b" if status == "Tidak Selaras" else "#854d0e")

        status_p = Paragraph(
            f"<b>{status.upper()}</b>",
            ParagraphStyle("StatCell", parent=body_style, textColor=colors.HexColor(status_color)),
        )

        internal_desc = f"<b>{c.get('id', '')}</b><br/>{c.get('pasal', '')}: {c.get('judul_klausul', '')}"
        external_desc = f"<b>{c.get('regulasi_terkait', '')}</b><br/>{c.get('pasal_regulasi', '')}"

        findings_data.append([
            Paragraph(internal_desc, body_style),
            Paragraph(external_desc, body_style),
            status_p,
            Paragraph(c.get("reasoning", "-"), body_style),
            Paragraph(c.get("rekomendasi", "-"), body_style),
        ])

    findings_table = Table(findings_data, colWidths=[100, 100, 65, 135, 120])
    findings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003d79")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(findings_table)
    elements.append(Spacer(1, 16))

    # 5. Lembar Pengesahan / Catatan Akhir
    elements.append(Paragraph("3. Catatan Implementasi & Kepatuhan", section_title_style))
    notes_text = (
        "Laporan audit ini dihasilkan secara otomatis melalui sistem SELARASKAN MDAB berbasis analisis semantik kepatuhan. "
        "Klausul yang berstatus Tidak Selaras berpotensi menimbulkan risiko hukum (legal risk) dan sanksi administratif dari "
        "regulator perbankan. Disarankan unit kerja pemilik kebijakan operasional segera menyusun rancangan addendum "
        "atau pembaruan Surat Edaran Direksi sesuai rekomendasi di atas."
    )
    elements.append(Paragraph(notes_text, body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

