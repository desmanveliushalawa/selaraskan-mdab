"""
generate_samples.py
Skrip untuk membuat berkas dokumen pengujian sample (.docx dan .pdf)
berisi struktur resmi peraturan internal Bank Mandiri.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


DOC_TITLE = "PETUNJUK OPERASIONAL BANK MANDIRI"
DOC_SUBTITLE = "PO-DIR/IT/042/2024: TATA KELOLA KETAHANAN SIBER, MANAJEMEN DATA, DAN OPERASIONAL PERBANKAN DIGITAL"

SECTIONS = [
    {
        "bab": "BAB I KETENTUAN UMUM",
        "pasal": "Pasal 1",
        "judul": "Ketentuan Pokok dan Ruang Lingkup",
        "ayat": "(1) Petunjuk Operasional ini mengatur standar teknis tata kelola ketahanan siber, manajemen perlindungan data nasabah, dan kelangsungan operasional layanan perbankan digital di lingkungan PT Bank Mandiri (Persero) Tbk.",
    },
    {
        "bab": "BAB II PENGAMANAN DATA DAN PRIVASI NASABAH",
        "pasal": "Pasal 4",
        "judul": "Pengamanan Enkripsi Data Sensitif Nasabah",
        "ayat": "(1) Setiap data rahasia perbankan dan data sensitif nasabah wajib dienkripsi pada saat transmisi menggunakan protokol TLS 1.3 dan pada saat diam (at-rest) menggunakan algoritma standar Advanced Encryption Standard 256-bit (AES-256).",
    },
    {
        "bab": "BAB II PENGAMANAN DATA DAN PRIVASI NASABAH",
        "pasal": "Pasal 7",
        "judul": "Batas Waktu Pelaporan Insiden Kebocoran Data Pribadi",
        "ayat": "(1) Apabila terjadi insiden kegagalan pelindungan atau dugaan kebocoran data pribadi nasabah, Unit Kerja Pengelola Data wajib menyampaikan pemberitahuan tertulis kepada nasabah paling lambat 14 (empat belas) hari kerja terhitung sejak insiden teridentifikasi.",
    },
    {
        "bab": "BAB III KELANGSUNGAN OPERASIONAL DAN BCP",
        "pasal": "Pasal 12",
        "judul": "Recovery Time Objective (RTO) Pusat Pemulihan Bencana",
        "ayat": "(1) Recovery Time Objective (RTO) untuk pemulihan sistem aplikasi kritikal perbankan pada Pusat Pemulihan Bencana (Disaster Recovery Center/DRC) ditetapkan paling lama 4 (empat) jam sejak status darurat atau bencana dinyatakan aktif oleh Komite Manajemen Krisis.",
    },
    {
        "bab": "BAB IV PENEMPATAN PUSAT DATA DAN CLOUD COMPUTING",
        "pasal": "Pasal 18",
        "judul": "Penempatan Data Transaksi dan Log Perbankan",
        "ayat": "(1) Bank dapat menempatkan pusat data operasional dan seluruh cadangan log transaksi finansial nasabah pada penyedia layanan komputasi awan (cloud) pihak ketiga yang lokasi server fisiknya berada di luar wilayah yurisdiksi Republik Indonesia tanpa persetujuan khusus regulator.",
    },
    {
        "bab": "BAB V PEMANTAUAN DAN OPERASI KEAMANAN SIBER",
        "pasal": "Pasal 22",
        "judul": "Operasional Security Operations Center (SOC)",
        "ayat": "(1) Bank wajib mengoperasikan Security Operations Center (SOC) selama 24 (dua puluh empat) jam sehari dan 7 (tujuh) hari seminggu secara berkesinambungan guna melakukan pemantauan proaktif, deteksi dini, dan penanganan anomali keamanan siber.",
    },
    {
        "bab": "BAB VI PENGUJIAN KEAMANAN SISTEM ELEKTRONIK",
        "pasal": "Pasal 26",
        "judul": "Uji Penetrasi dan Asesmen Kerentanan Berkala",
        "ayat": "(1) Pengujian keamanan siber melalui vulnerability assessment dan penetration testing (pentest) pada seluruh infrastruktur sistem elektronik bank wajib dilakukan oleh pihak independen bersertifikasi minimal 1 (satu) kali dalam 1 (satu) tahun.",
    },
]


def create_docx(filepath: str):
    doc = Document()
    
    # Page Margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run(DOC_TITLE)
    run_title.font.name = "Arial"
    run_title.font.size = Pt(14)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0, 61, 121)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run(DOC_SUBTITLE)
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph() # Spacer

    current_bab = ""
    for sec in SECTIONS:
        if sec["bab"] != current_bab:
            current_bab = sec["bab"]
            p_bab = doc.add_paragraph()
            p_bab.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_bab = p_bab.add_run(f"\n{current_bab}")
            run_bab.font.name = "Arial"
            run_bab.font.size = Pt(11)
            run_bab.font.bold = True
            run_bab.font.color.rgb = RGBColor(0, 61, 121)

        p_pasal = doc.add_paragraph()
        p_pasal.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_pasal = p_pasal.add_run(sec["pasal"])
        run_pasal.font.name = "Arial"
        run_pasal.font.size = Pt(10.5)
        run_pasal.font.bold = True

        p_ayat = doc.add_paragraph()
        p_ayat.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run_ayat = p_ayat.add_run(sec["ayat"])
        run_ayat.font.name = "Arial"
        run_ayat.font.size = Pt(10)

    doc.save(filepath)
    print(f"Berhasil membuat berkas DOCX: {filepath}")


def create_pdf(filepath: str):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "CustomTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#003d79"),
        alignment=1, # Center
        spaceAfter=4,
    )
    style_sub = ParagraphStyle(
        "CustomSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=1, # Center
        spaceAfter=15,
    )
    style_bab = ParagraphStyle(
        "CustomBab",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#003d79"),
        alignment=1, # Center
        spaceBefore=12,
        spaceAfter=4,
    )
    style_pasal = ParagraphStyle(
        "CustomPasal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=1, # Center
        spaceBefore=6,
        spaceAfter=4,
    )
    style_ayat = ParagraphStyle(
        "CustomAyat",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        alignment=4, # Justify
        spaceAfter=8,
    )

    story = [
        Paragraph(DOC_TITLE, style_title),
        Paragraph(DOC_SUBTITLE, style_sub),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003d79"), spaceAfter=10),
    ]

    current_bab = ""
    for sec in SECTIONS:
        if sec["bab"] != current_bab:
            current_bab = sec["bab"]
            story.append(Paragraph(current_bab, style_bab))
        story.append(Paragraph(sec["pasal"], style_pasal))
        story.append(Paragraph(sec["ayat"], style_ayat))

    doc.build(story)
    print(f"Berhasil membuat berkas PDF: {filepath}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    docx_path = os.path.join("data", "sample_kebijakan_internal_mandiri.docx")
    pdf_path = os.path.join("data", "sample_kebijakan_internal_mandiri.pdf")
    create_docx(docx_path)
    create_pdf(pdf_path)
