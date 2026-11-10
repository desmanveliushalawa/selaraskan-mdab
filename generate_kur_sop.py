"""
generate_kur_sop.py
Menghasilkan berkas SOP resmi internal Bank Mandiri terkait Penyaluran KUR:
'dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.docx'
'dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.pdf'
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


DOC_TITLE = "STANDAR OPERASIONAL PROSEDUR (SOP) BANK MANDIRI"
DOC_SUBTITLE = "SOP-DIR/MSME/018/2024: TATA CARA DAN PERSYARATAN PENYALURAN KREDIT USAHA RAKYAT (KUR)"

KUR_SECTIONS = [
    {
        "bab": "BAB I KETENTUAN UMUM",
        "pasal": "Pasal 1",
        "judul": "Ketentuan Pokok dan Sasaran Program",
        "ayat": "(1) Standar Operasional Prosedur ini mengatur tata cara, persyaratan kelayakan calon debitur, verifikasi data, dan tata kelola penyaluran Kredit Usaha Rakyat (KUR) bagi pelaku usaha mikro, kecil, dan menengah pada seluruh jaringan kantor PT Bank Mandiri (Persero) Tbk.",
    },
    {
        "bab": "BAB I KETENTUAN UMUM",
        "pasal": "Pasal 3",
        "judul": "Kriteria Kelayakan Usaha Produktif",
        "ayat": "(1) Calon debitur penerima fasilitas KUR wajib memiliki usaha produktif dan layak dibiayai yang telah aktif beroperasi secara terus-menerus paling singkat selama 6 (enam) bulan, dibuktikan dengan Nomor Induk Berusaha (NIB) atau Surat Keterangan Usaha (SKU) dari pejabat berwenang.",
    },
    {
        "bab": "BAB II SKEMA PLAFON DAN PENETAPAN SUKU BUNGA",
        "pasal": "Pasal 5",
        "judul": "Batasan Plafon dan Jangka Waktu Pembiayaan",
        "ayat": "(1) Penyaluran KUR Mikro diberikan dengan plafon di atas Rp 10.000.000 (sepuluh juta rupiah) sampai dengan Rp 100.000.000 (seratus juta rupiah) dengan jangka waktu Kredit Modal Kerja maksimal 3 (tiga) tahun atau Kredit Investasi maksimal 5 (lima) tahun.",
    },
    {
        "bab": "BAB II SKEMA PLAFON DAN PENETAPAN SUKU BUNGA",
        "pasal": "Pasal 7",
        "judul": "Penetapan Suku Bunga dan Marjin Pinjaman",
        "ayat": "(1) Suku bunga pinjaman KUR Mikro dan KUR Kecil ditetapkan flat sebesar 6% (enam persen) efektif per tahun untuk seluruh siklus pinjaman debitur, tanpa memberlakukan skema kenaikan suku bunga berjenjang pada pengajuan pinjaman berulang.",
    },
    {
        "bab": "BAB III KETENTUAN PERSYARATAN AGUNAN",
        "pasal": "Pasal 9",
        "judul": "Persyaratan Agunan Tambahan bagi Penerima KUR",
        "ayat": "(1) Untuk memitigasi risiko kredit bermasalah, Unit Bisnis Mikro Bank Mandiri wajib meminta agunan tambahan berupa sertifikat tanah/bangunan atau BPKB kendaraan bermotor terhadap seluruh permohonan pinjaman KUR dengan plafon di atas Rp 50.000.000 (lima puluh juta rupiah).",
    },
    {
        "bab": "BAB IV VERIFIKASI DATA DAN KELAYAKAN SISTEM",
        "pasal": "Pasal 12",
        "judul": "Verifikasi Basis Data SIKP Kementerian Keuangan",
        "ayat": "(1) Sebelum penerbitan persetujuan kredit (SP3K), pejabat pemutus kredit wajib melakukan pemeriksaan status calon debitur pada Sistem Informasi Kredit Program (SIKP) Kementerian Keuangan guna memastikan calon debitur belum pernah menerima fasilitas subsidi suku bunga KUR sejenis yang melampaui batas akumulasi plafon.",
    },
    {
        "bab": "BAB V KEPATUHAN DAN PENGAWASAN REGULASI",
        "pasal": "Pasal 16",
        "judul": "Penagihan dan Kerja Sama Penjaminan Kredit",
        "ayat": "(1) Terhadap fasilitas pinjaman KUR yang mengalami penurunan kualitas menjadi kurang lancar atau macet, bank melakukan upaya penagihan sesuai ketentuan perbankan dan mengajukan klaim penjaminan kredit kepada Perusahaan Penjamin yang ditunjuk Pemerintah paling lambat 60 (enam puluh) hari kalender sejak klaim memenuhi syarat.",
    },
]


def create_kur_docx(filepath: str):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run(DOC_TITLE)
    run_title.font.name = "Arial"
    run_title.font.size = Pt(14)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0, 61, 121)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run(DOC_SUBTITLE)
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph()

    current_bab = ""
    for sec in KUR_SECTIONS:
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


def create_kur_pdf(filepath: str):
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
        "KurTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#003d79"),
        alignment=1,
        spaceAfter=4,
    )
    style_sub = ParagraphStyle(
        "KurSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=15,
    )
    style_bab = ParagraphStyle(
        "KurBab",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#003d79"),
        alignment=1,
        spaceBefore=12,
        spaceAfter=4,
    )
    style_pasal = ParagraphStyle(
        "KurPasal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=1,
        spaceBefore=6,
        spaceAfter=4,
    )
    style_ayat = ParagraphStyle(
        "KurAyat",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        alignment=4,
        spaceAfter=8,
    )

    story = [
        Paragraph(DOC_TITLE, style_title),
        Paragraph(DOC_SUBTITLE, style_sub),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003d79"), spaceAfter=10),
    ]

    current_bab = ""
    for sec in KUR_SECTIONS:
        if sec["bab"] != current_bab:
            current_bab = sec["bab"]
            story.append(Paragraph(current_bab, style_bab))
        story.append(Paragraph(sec["pasal"], style_pasal))
        story.append(Paragraph(sec["ayat"], style_ayat))

    doc.build(story)
    print(f"Berhasil membuat berkas PDF: {filepath}")


if __name__ == "__main__":
    dest_dir = "dokumen_internal_mandiri"
    os.makedirs(dest_dir, exist_ok=True)
    docx_path = os.path.join(dest_dir, "SOP_Penyaluran_KUR_Bank_Mandiri.docx")
    pdf_path = os.path.join(dest_dir, "SOP_Penyaluran_KUR_Bank_Mandiri.pdf")
    create_kur_docx(docx_path)
    create_kur_pdf(pdf_path)
