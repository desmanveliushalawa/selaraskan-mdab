"""
app.py
Aplikasi Uji Keselarasan Regulasi Perbankan (SELARASKAN MDAB)
Komparasi Petunjuk Operasional Bank Mandiri terhadap Regulasi Regulator (POJK, BI, UU PDP)
Desain institusional berbasis arsitektur legal-tech, bebas dari ornamen AI generik.
"""

import io
import json
import os
import textwrap
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.diff_highlighter import render_side_by_side_diff_html
from engine.alignment_engine import (
    load_benchmark_data,
    calculate_compliance_metrics,
    evaluate_custom_clause_alignment,
)
from engine.legal_parser import extract_raw_text, parse_legal_structure
from engine.report_generator import generate_compliance_pdf_report
from engine.semantic_retriever import get_default_retriever


def render_html(html_str: str):
    """Merender HTML ke Streamlit tanpa risiko terpotong menjadi kode blok markdown."""
    clean_lines = [line.lstrip() for line in html_str.splitlines() if line.strip()]
    clean_html = "\n".join(clean_lines)
    st.markdown(clean_html, unsafe_allow_html=True)


def filter_clause_list(clauses_list: list, status_filter: str, search_query: str) -> list:
    """Menyaring daftar klausul berdasarkan status kepatuhan dan kata kunci pencarian."""
    result = list(clauses_list)

    if status_filter == "Hanya Tidak Selaras (Prioritas Risiko)":
        result = [c for c in result if c.get("status") == "Tidak Selaras"]
    elif status_filter == "Hanya Selaras":
        result = [c for c in result if c.get("status") == "Selaras"]
    elif status_filter == "Hanya Netral":
        result = [c for c in result if c.get("status") == "Netral"]

    if search_query and search_query.strip():
        q_tokens = search_query.strip().lower().split()
        def matches(c):
            haystack = " ".join([
                str(c.get("bab", "")),
                str(c.get("pasal", "")),
                str(c.get("ayat", "")),
                str(c.get("judul_klausul", "")),
                str(c.get("teks_internal", "")),
                str(c.get("text", "")),
                str(c.get("regulasi_terkait", "")),
                str(c.get("pasal_regulasi", "")),
                str(c.get("teks_regulasi", "")),
                str(c.get("reasoning", "")),
                str(c.get("status", "")),
            ]).lower()
            return all(token in haystack for token in q_tokens)
        result = [c for c in result if matches(c)]

    return result


# Konfigurasi Halaman Institusional
st.set_page_config(
    page_title="SELARASKAN MDAB : Uji Keselarasan Regulasi",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Bersih dan Terstruktur: Standar Desain Perbankan & Legal Tech
render_html(
    """
    <style>
    /* Tipografi Dasar */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
    }

    /* Header Institusional */
    .brand-header {
        background-color: #ffffff;
        border-bottom: 2px solid #003d79;
        padding: 16px 0 14px 0;
        margin-bottom: 20px;
    }
    .brand-title {
        font-size: 20px;
        font-weight: 700;
        color: #003d79;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #475569;
        margin-top: 4px;
        line-height: 1.4;
    }
    .brand-badge {
        font-size: 11px;
        color: #475569;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 4px 8px;
        border-radius: 4px;
        text-align: right;
    }

    /* Kartu Ringkasan Metrik */
    .metric-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 12px 16px;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-number {
        font-size: 22px;
        font-weight: 700;
        margin: 4px 0 2px 0;
    }
    .metric-desc {
        font-size: 11px;
        color: #64748b;
    }

    /* Kartu Klausul Hukum */
    .legal-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .legal-card:hover {
        border-color: #94a3b8;
    }
    .legal-meta {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 4px;
    }
    .legal-title {
        font-size: 14px;
        font-weight: 700;
        color: #003d79;
        margin: 0 0 8px 0;
    }
    .reference-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 12px;
        color: #334155;
        margin-bottom: 10px;
    }
    .reasoning-text {
        font-size: 12px;
        color: #1e293b;
        line-height: 1.5;
        margin-bottom: 10px;
    }

    /* Badge Status */
    .badge-selaras {
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .badge-tidaksaras {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .badge-netral {
        background-color: #fefce8;
        color: #854d0e;
        border: 1px solid #fef08a;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* Tombol Aksi */
    .stButton > button {
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }
    </style>
    """
)


# Dialog Perbandingan Before-After
@st.dialog("Komparasi Redaksional Klausul (Before-After)", width="large")
def show_diff_dialog(clause: dict):
    st.caption(f"ID Klausul: {clause.get('id', '')} : {clause.get('judul_klausul', '')}")

    diff_html = render_side_by_side_diff_html(
        title_internal=f"{clause.get('bab', '')} • {clause.get('pasal', '')}",
        text_internal=clause.get("teks_internal", ""),
        title_regulasi=f"{clause.get('regulasi_terkait', '')} • {clause.get('pasal_regulasi', '')}",
        text_regulasi=clause.get("teks_regulasi", ""),
        status=clause.get("status", "Netral"),
        reasoning=clause.get("reasoning", ""),
    )
    render_html(diff_html)

    rekomendasi = clause.get("rekomendasi", "")
    if rekomendasi:
        render_html(
            f"""
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 10px 12px; margin-top: 12px; font-size: 12px; color: #1e293b;">
                <strong>Rekomendasi Tindakan:</strong> {rekomendasi}
            </div>
            """
        )

    if st.button("Tutup Dialog", use_container_width=True):
        st.rerun()


# Pemuatan Data Benchmark Simulasi
@st.cache_data
def get_benchmark_data():
    return load_benchmark_data()

benchmark_data = get_benchmark_data()
demo_doc_info = benchmark_data["internal_document"]
demo_clauses = benchmark_data["clauses"]
demo_metrics = calculate_compliance_metrics(demo_clauses)


# Sidebar Kontrol & Pemilihan Sumber Dokumen
with st.sidebar:
    st.markdown("### Sumber Dokumen Evaluasi")
    default_source_idx = 1 if "uploaded_analysis" in st.session_state else 0
    source_mode = st.radio(
        "Pilih Data untuk Dianalisis:",
        options=["Contoh Studi Kasus (Bank Mandiri)", "Unggah Dokumen Baru (.docx / .pdf)"],
        index=default_source_idx,
        help="Gunakan 'Contoh Studi Kasus' untuk melihat simulasi awal, atau 'Unggah Dokumen Baru' untuk memproses dokumen Anda sendiri.",
    )

    st.markdown("---")
    st.markdown("### Regulasi Acuan Kepatuhan")
    for reg in benchmark_data["external_benchmark"]["regulations"]:
        st.markdown(f"• <span style='font-size: 12px; color: #334155;'>{reg}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Filter Penelusuran")
    filter_status = st.selectbox(
        "Status Keselarasan:",
        options=["Semua Status", "Hanya Tidak Selaras (Prioritas Risiko)", "Hanya Selaras", "Hanya Netral"],
        index=0,
    )

    search_keyword = st.text_input("Pencarian Pasal atau Kata Kunci:", placeholder="Contoh: enkripsi, drc, cloud...")

    st.markdown("---")
    st.markdown("### Ekspor Laporan")
    
    # Download button untuk mode saat ini
    if source_mode == "Contoh Studi Kasus (Bank Mandiri)":
        export_clauses = demo_clauses
        export_doc_info = demo_doc_info
        export_metrics = demo_metrics
    elif "uploaded_analysis" in st.session_state:
        export_clauses = st.session_state["uploaded_analysis"]["clauses"]
        export_doc_info = st.session_state["uploaded_analysis"]["doc_info"]
        export_metrics = st.session_state["uploaded_analysis"]["metrics"]
    else:
        export_clauses = []
        export_doc_info = {"title": "Belum ada dokumen", "version": "v1.0", "subject": "-", "issued_date": "-"}
        export_metrics = calculate_compliance_metrics([])

    if export_clauses:
        df_export = pd.DataFrame([
            {
                "ID": c.get("id", ""),
                "Bab": c.get("bab", ""),
                "Pasal Internal": c.get("pasal", ""),
                "Judul": c.get("judul_klausul", ""),
                "Status": c.get("status", ""),
                "Regulasi Terkait": c.get("regulasi_terkait", ""),
                "Pasal Regulasi": c.get("pasal_regulasi", ""),
                "Pertimbangan Hukum": c.get("reasoning", ""),
                "Rekomendasi": c.get("rekomendasi", ""),
            }
            for c in export_clauses
        ])
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)

        st.download_button(
            label="Unduh Laporan Formal (PDF)",
            data=generate_compliance_pdf_report(export_doc_info, benchmark_data["external_benchmark"], export_clauses, export_metrics),
            file_name="Laporan_Resmi_Audit_Regulasi_SELARASKAN_MDAB.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.download_button(
            label="Unduh Rekapitulasi Data (CSV)",
            data=csv_buffer.getvalue(),
            file_name="Laporan_Audit_Keselarasan_SELARASKAN_MDAB.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.caption("Unggah dokumen terlebih dahulu untuk mengunduh laporan.")


# Header Utama Institusional
current_version = demo_doc_info['version'] if source_mode == "Contoh Studi Kasus (Bank Mandiri)" else (
    st.session_state["uploaded_analysis"]["doc_info"]["version"] if "uploaded_analysis" in st.session_state else "Menunggu Unggahan"
)
render_html(
    f"""
    <div class="brand-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 class="brand-title">SELARASKAN MDAB : Uji Keselarasan Regulasi Operasional</h1>
                <div class="brand-subtitle">
                    Audit Kepatuhan Kebijakan Internal Bank Mandiri terhadap Ketentuan Regulator (POJK, Bank Indonesia, UU PDP)
                </div>
            </div>
            <div class="brand-badge">
                <div>Dokumen: {current_version}</div>
                <div>Mode: {'Contoh Demo' if source_mode == "Contoh Studi Kasus (Bank Mandiri)" else 'Unggah Sendiri'}</div>
            </div>
        </div>
    </div>
    """
)


# Tab Navigasi Utama
tab_evaluasi, tab_unggah, tab_uji, tab_panduan = st.tabs([
    "Matriks Keselarasan Dokumen",
    "Unggah & Parsing Dokumen",
    "Uji Klausul Mandiri",
    "Arsitektur & Konsep Sistem",
])


# TAB 1: Matriks Keselarasan Dokumen
with tab_evaluasi:
    # Tentukan data klausul dan metrik yang aktif
    if source_mode == "Contoh Studi Kasus (Bank Mandiri)":
        active_doc_info = demo_doc_info
        active_clauses = demo_clauses
        active_metrics = demo_metrics
        st.info("Mode Pratinjau: Menampilkan contoh simulasi (Petunjuk Operasional No. PO-DIR/IT/042/2024 Bank Mandiri). Untuk menganalisis dokumen Anda sendiri dari awal, pilih 'Unggah Dokumen Baru' di sidebar kiri.")
    else:
        if "uploaded_analysis" in st.session_state:
            active_doc_info = st.session_state["uploaded_analysis"]["doc_info"]
            active_clauses = st.session_state["uploaded_analysis"]["clauses"]
            active_metrics = st.session_state["uploaded_analysis"]["metrics"]
            st.success(f"Mode Dokumen Unggahan Aktif: Menampilkan hasil evaluasi dari berkas '{active_doc_info['title']}'.")
        else:
            active_doc_info = None
            active_clauses = []
            active_metrics = None

    if active_clauses and active_metrics:
        # Ringkasan Eksekutif & Donut Chart
        col_summary, col_pie = st.columns([1.6, 1.2])

        with col_summary:
            st.markdown("#### Ringkasan Hasil Evaluasi Dokumen")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)

            with kpi1:
                render_html(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Total Klausul</div>
                        <div class="metric-number" style="color: #003d79;">{active_metrics['total']}</div>
                        <div class="metric-desc">Klausul Dianalisis</div>
                    </div>
                    """
                )
            with kpi2:
                render_html(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Selaras</div>
                        <div class="metric-number" style="color: #166534;">{active_metrics['selaras']['count']}</div>
                        <div class="metric-desc">{active_metrics['selaras']['pct']}% Sesuai Standar</div>
                    </div>
                    """
                )
            with kpi3:
                render_html(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Tidak Selaras</div>
                        <div class="metric-number" style="color: #991b1b;">{active_metrics['tidak_selaras']['count']}</div>
                        <div class="metric-desc">{active_metrics['tidak_selaras']['pct']}% Perlu Revisi</div>
                    </div>
                    """
                )
            with kpi4:
                render_html(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Netral</div>
                        <div class="metric-number" style="color: #854d0e;">{active_metrics['netral']['count']}</div>
                        <div class="metric-desc">{active_metrics['netral']['pct']}% Aturan Teknis</div>
                    </div>
                    """
                )

            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 10px 14px; margin-top: 12px; font-size: 12px; color: #334155; line-height: 1.5;">
                    <strong>Catatan Kepatuhan:</strong> Dari {active_metrics['total']} klausul yang dievaluasi, terdeteksi {active_metrics['tidak_selaras']['count']} klausul yang memiliki deviasi normatif terhadap regulasi rujukan dan direkomendasikan untuk segera dilakukan addendum/penyesuaian kebijakan.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_pie:
            st.markdown("#### Proporsi Keselarasan Norma")
            labels = ["Selaras", "Tidak Selaras", "Netral"]
            values = [active_metrics["selaras"]["count"], active_metrics["tidak_selaras"]["count"], active_metrics["netral"]["count"]]
            colors = ["#166534", "#991b1b", "#ca8a04"]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.60,
                marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
                textinfo="percent+value",
                hoverinfo="label+value+percent",
                textfont_size=11,
            )])
            fig.update_layout(
                showlegend=True,
                height=180,
                margin=dict(l=10, r=10, t=5, b=5),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=11)),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 16px 0 20px 0;'>", unsafe_allow_html=True)

        # Filter klausul menggunakan helper universal
        filtered_clauses = filter_clause_list(active_clauses, filter_status, search_keyword)

        col_nav, col_content = st.columns([1.1, 1.9])

        with col_nav:
            st.markdown("##### Struktur Hierarki Dokumen")
            babs = {}
            for c in filtered_clauses:
                babs.setdefault(c.get("bab", "Umum"), []).append(c)

            if not babs:
                st.caption("Tidak ada Bab yang cocok dengan kriteria filter.")
            else:
                for bab_name, items in babs.items():
                    with st.expander(f"{bab_name} ({len(items)})", expanded=True):
                        for item in items:
                            badge_style = (
                                "badge-selaras" if item["status"] == "Selaras"
                                else ("badge-tidaksaras" if item["status"] == "Tidak Selaras" else "badge-netral")
                            )
                            render_html(
                                f"""
                                <div style="font-size: 12px; margin-bottom: 8px; padding: 4px 0 4px 6px; border-left: 2px solid #cbd5e1;">
                                    <div style="font-weight: 600; color: #003d79;">{item.get('pasal', '')}</div>
                                    <div style="font-size: 11px; color: #475569; margin: 2px 0;">{item.get('judul_klausul', '')}</div>
                                    <span class="{badge_style}">{item.get('status', '')}</span>
                                </div>
                                """
                            )

        with col_content:
            st.markdown(f"##### Daftar Klausul & Hasil Evaluasi ({len(filtered_clauses)} dari {len(active_clauses)} Klausul)")

            if search_keyword.strip() or filter_status != "Semua Status":
                active_filter_msg = []
                if search_keyword.strip():
                    active_filter_msg.append(f"Kata Kunci: \"{search_keyword.strip()}\"")
                if filter_status != "Semua Status":
                    active_filter_msg.append(f"Status: {filter_status}")
                st.caption(f"Filter Aktif: {', '.join(active_filter_msg)}")

            if not filtered_clauses:
                st.info("Tidak ada klausul yang sesuai dengan filter pencarian.")
            else:
                for idx, clause in enumerate(filtered_clauses):
                    status = clause["status"]
                    badge_class = (
                        "badge-selaras" if status == "Selaras"
                        else ("badge-tidaksaras" if status == "Tidak Selaras" else "badge-netral")
                    )

                    card_html = f"""
                    <div class="legal-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div class="legal-meta">{clause.get('id', '')} : {clause.get('bab', '')}</div>
                                <h3 class="legal-title">{clause.get('pasal', '')}: {clause.get('judul_klausul', '')}</h3>
                            </div>
                            <span class="{badge_class}">{status.upper()}</span>
                        </div>
                        <div class="reference-box">
                            <strong>Ketentuan Acuan:</strong> {clause.get('regulasi_terkait', '')} ({clause.get('pasal_regulasi', '')})
                        </div>
                        <div class="reasoning-text">
                            <strong>Pertimbangan Hukum:</strong> {clause.get('reasoning', '')}
                        </div>
                    </div>
                    """
                    render_html(card_html)

                    btn_col1, _ = st.columns([1.6, 2.4])
                    with btn_col1:
                        if st.button(
                            "Lihat Komparasi Before-After",
                            key=f"btn_diff_{clause.get('id', '')}_{idx}",
                            use_container_width=True,
                        ):
                            show_diff_dialog(clause)

                    st.write("")
    else:
        # Tampilan kosong terarah (Clean Empty State)
        render_html(
            """
            <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; padding: 40px 20px; text-align: center; color: #475569; margin: 20px 0;">
                <h4 style="color: #003d79; margin-bottom: 8px; font-size: 16px;">Belum Ada Dokumen yang Diunggah</h4>
                <p style="font-size: 13px; max-width: 580px; margin: 0 auto 16px auto; line-height: 1.5; color: #64748b;">
                    Anda saat ini berada pada mode <strong>Unggah Dokumen Baru</strong>. Silakan buka tab <strong>"Unggah & Parsing Dokumen"</strong> di atas untuk mengunggah berkas Word (.docx) atau PDF regulasi Anda, atau alihkan pilihan ke <strong>"Contoh Studi Kasus (Bank Mandiri)"</strong> pada menu di sidebar kiri untuk melihat contoh simulasi.
                </p>
            </div>
            """
        )


# TAB 2: Unggah & Parsing Dokumen (Legal Parser)
with tab_unggah:
    st.markdown("#### Unggah & Ekstraksi Dokumen Regulasi (Legal Parser)")
    st.markdown(
        "<span style='font-size: 13px; color: #475569;'>"
        "Modul ini mengekstrak struktur hierarki Bab, Pasal, dan Ayat dari berkas dokumen hukum asli (.docx, .pdf, atau .txt) "
        "sebelum dijalankan pada engine uji keselarasan."
        "</span>",
        unsafe_allow_html=True,
    )

    # Box Unduh Berkas Contoh Pengujian
    render_html(
        """
        <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px; padding: 12px 16px; margin: 12px 0 16px 0;">
            <div style="font-size: 13px; font-weight: 600; color: #003d79; margin-bottom: 4px;">
                Pilih Berkas Kebijakan Resmi Bank Mandiri untuk Pengujian:
            </div>
            <div style="font-size: 12px; color: #475569; line-height: 1.4;">
                Unduh salah satu berkas peraturan resmi di bawah ini (tersedia dokumen Kredit Usaha Rakyat / KUR dan Tata Kelola TI Bank Mandiri), lalu unggah kembali melalui kotak uploader di bawah untuk menjalankan ekstraksi dan audit keselarasan:
            </div>
        </div>
        """
    )

    col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)

    # 1. SOP Penyaluran KUR Bank Mandiri
    kur_docx_path = "dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.docx"
    kur_pdf_path = "dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.pdf"
    riplay_kur_path = "dokumen_internal_mandiri/RIPLAY_Ketentuan_KUR_Bank_Mandiri.pdf"
    cyber_pdf_path = "data/sample_kebijakan_internal_mandiri.pdf"

    with col_dl1:
        if os.path.exists(kur_pdf_path):
            with open(kur_pdf_path, "rb") as f_kpdf:
                st.download_button(
                    label="SOP KUR Mandiri (PDF)",
                    data=f_kpdf.read(),
                    file_name="SOP_Penyaluran_KUR_Bank_Mandiri.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
    with col_dl2:
        if os.path.exists(kur_docx_path):
            with open(kur_docx_path, "rb") as f_kdocx:
                st.download_button(
                    label="SOP KUR Mandiri (DOCX)",
                    data=f_kdocx.read(),
                    file_name="SOP_Penyaluran_KUR_Bank_Mandiri.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
    with col_dl3:
        if os.path.exists(riplay_kur_path):
            with open(riplay_kur_path, "rb") as f_riplay:
                st.download_button(
                    label="RIPLAY KUR Mandiri (PDF)",
                    data=f_riplay.read(),
                    file_name="RIPLAY_Ketentuan_KUR_Bank_Mandiri.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
    with col_dl4:
        if os.path.exists(cyber_pdf_path):
            with open(cyber_pdf_path, "rb") as f_cpdf:
                st.download_button(
                    label="Kebijakan TI Siber (PDF)",
                    data=f_cpdf.read(),
                    file_name="sample_kebijakan_internal_mandiri.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    st.write("")

    uploaded_file = st.file_uploader(
        "Pilih berkas dokumen peraturan internal atau regulasi acuan:",
        type=["docx", "pdf", "txt"],
        help="Mendukung dokumen Microsoft Word (.docx), PDF standar (.pdf), atau teks mentah (.txt)",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name
        file_size_kb = round(len(file_bytes) / 1024, 1)

        with st.spinner("Mengekstrak teks dan menganalisis hierarki hukum Indonesia..."):
            try:
                raw_text = extract_raw_text(file_bytes, filename)
                parsed_doc = parse_legal_structure(raw_text)

                st.success(f"Berkas '{filename}' berhasil di-parse.")

                # Tabel Metadata Hasil Ekstraksi
                st.markdown("##### Metadata Dokumen yang Diekstraksi")
                meta_cols = st.columns(4)
                with meta_cols[0]:
                    render_html(
                        f"""
                        <div class="metric-box">
                            <div class="metric-label">Nama Berkas</div>
                            <div style="font-size: 13px; font-weight: 600; color: #003d79; margin: 4px 0;">{filename}</div>
                            <div class="metric-desc">Ukuran: {file_size_kb} KB</div>
                        </div>
                        """
                    )
                with meta_cols[1]:
                    render_html(
                        f"""
                        <div class="metric-box">
                            <div class="metric-label">Total Bab Terdeteksi</div>
                            <div class="metric-number" style="color: #003d79;">{parsed_doc['total_bab']}</div>
                            <div class="metric-desc">Struktur Utama</div>
                        </div>
                        """
                    )
                with meta_cols[2]:
                    render_html(
                        f"""
                        <div class="metric-box">
                            <div class="metric-label">Total Pasal</div>
                            <div class="metric-number" style="color: #003d79;">{parsed_doc['total_pasal']}</div>
                            <div class="metric-desc">Norma Terpisah</div>
                        </div>
                        """
                    )
                with meta_cols[3]:
                    render_html(
                        f"""
                        <div class="metric-box">
                            <div class="metric-label">Total Ayat / Butir</div>
                            <div class="metric-number" style="color: #003d79;">{parsed_doc['total_ayat']}</div>
                            <div class="metric-desc">Klausul Spesifik</div>
                        </div>
                        """
                    )

                st.markdown(f"**Estimasi Judul Regulasi:** `{parsed_doc['title']}`")

                # Daftar Klausul yang Berhasil Diekstraksi
                st.markdown("##### Rincian Klausul yang Terdaftar")
                if parsed_doc["clauses"]:
                    display_parsed_clauses = filter_clause_list(parsed_doc["clauses"], "Semua Status", search_keyword)
                    if search_keyword.strip():
                        st.caption(f"Menampilkan {len(display_parsed_clauses)} dari {len(parsed_doc['clauses'])} klausul untuk kata kunci: \"{search_keyword.strip()}\"")

                    df_parsed = pd.DataFrame([
                        {
                            "No": i + 1,
                            "Bab": c["bab"],
                            "Pasal": c["pasal"],
                            "Ayat / Butir": c["ayat"],
                            "Teks Klausul": (c["text"][:110] + "...") if len(c["text"]) > 110 else c["text"],
                        }
                        for i, c in enumerate(display_parsed_clauses)
                    ])
                    st.dataframe(df_parsed, use_container_width=True, hide_index=True)

                    # Aksi Eksekusi Audit Kepatuhan Otomatis
                    st.markdown("##### Evaluasi Keselarasan terhadap Regulasi Acuan")
                    if st.button("Jalankan Uji Keselarasan untuk Dokumen Ini", type="primary"):
                        with st.spinner("Mencocokkan klausul dengan korpus regulasi menggunakan Semantic Retrieval..."):
                            retriever = get_default_retriever()
                            eval_list = []
                            for i, c in enumerate(parsed_doc["clauses"]):
                                matches = retriever.retrieve_best_match(c["text"], top_k=1)
                                if matches and matches[0]["similarity_score"] > 0.05:
                                    ref_sample = matches[0]
                                    sim_pct = int(ref_sample["similarity_score"] * 100)
                                else:
                                    ref_sample = demo_clauses[i % len(demo_clauses)]
                                    sim_pct = 70

                                eval_res = evaluate_custom_clause_alignment(c["text"], ref_sample["teks_regulasi"])
                                eval_list.append({
                                    "id": f"UP-{i+1:03d}",
                                    "bab": c["bab"],
                                    "pasal": c["pasal"],
                                    "ayat": c["ayat"],
                                    "judul_klausul": f"{c['pasal']} {c['ayat']}",
                                    "teks_internal": c["text"],
                                    "regulasi_terkait": ref_sample["regulasi_terkait"],
                                    "pasal_regulasi": ref_sample["pasal_regulasi"],
                                    "teks_regulasi": ref_sample["teks_regulasi"],
                                    "similarity_pct": sim_pct,
                                    "status": eval_res["status"],
                                    "reasoning": eval_res["reasoning"],
                                    "rekomendasi": eval_res["rekomendasi"],
                                })

                            up_metrics = calculate_compliance_metrics(eval_list)
                            
                            # Simpan ke session state agar persisten dan Tab 1 otomatis sinkron
                            st.session_state["uploaded_analysis"] = {
                                "filename": filename,
                                "doc_info": {
                                    "title": parsed_doc["title"],
                                    "subject": f"Ekstraksi dari berkas {filename}",
                                    "version": "v1.0 (Unggahan)",
                                    "issued_date": "Terbaru",
                                },
                                "clauses": eval_list,
                                "metrics": up_metrics,
                            }
                            st.rerun()

                    # Render hasil evaluasi dari session state (persisten saat tombol dialog diklik)
                    if (
                        "uploaded_analysis" in st.session_state
                        and st.session_state["uploaded_analysis"].get("filename") == filename
                    ):
                        analysis = st.session_state["uploaded_analysis"]
                        saved_metrics = analysis["metrics"]
                        saved_clauses = analysis["clauses"]

                        display_eval_clauses = filter_clause_list(saved_clauses, filter_status, search_keyword)

                        st.success(
                            f"Audit selesai. Ditemukan {saved_metrics['selaras']['count']} Selaras, "
                            f"{saved_metrics['tidak_selaras']['count']} Tidak Selaras, "
                            f"{saved_metrics['netral']['count']} Netral. Hasil lengkap kini juga dapat dianalisis di Tab 1 (Matriks Keselarasan Dokumen)!"
                        )

                        if search_keyword.strip() or filter_status != "Semua Status":
                            st.info(f"Menampilkan {len(display_eval_clauses)} dari {len(saved_clauses)} klausul hasil evaluasi sesuai filter penelusuran.")

                        if not display_eval_clauses:
                            st.warning(f"Tidak ada klausul hasil evaluasi yang sesuai dengan filter kata kunci '{search_keyword.strip()}'.")
                        else:
                            for up_idx, item in enumerate(display_eval_clauses):
                                b_class = (
                                    "badge-selaras" if item["status"] == "Selaras"
                                    else ("badge-tidaksaras" if item["status"] == "Tidak Selaras" else "badge-netral")
                                )
                                up_card_html = f"""
                                <div class="legal-card">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                        <div>
                                            <div class="legal-meta">{item['bab']} • {item['pasal']} ({item['ayat']})</div>
                                            <h4 class="legal-title">{item['teks_internal'][:90]}...</h4>
                                        </div>
                                        <span class="{b_class}">{item['status'].upper()}</span>
                                    </div>
                                    <div class="reference-box">
                                        <strong>Ketentuan Acuan:</strong> {item['regulasi_terkait']} ({item['pasal_regulasi']}) • 
                                        <em>Relevansi Semantik: {item['similarity_pct']}%</em>
                                    </div>
                                    <div class="reasoning-text">
                                        <strong>Pertimbangan Hukum:</strong> {item['reasoning']}
                                    </div>
                                </div>
                                """
                                render_html(up_card_html)

                                up_btn_col, _ = st.columns([1.6, 2.4])
                                with up_btn_col:
                                    if st.button(
                                        "Lihat Komparasi Before-After",
                                        key=f"btn_up_diff_{item['id']}_{up_idx}",
                                        use_container_width=True,
                                    ):
                                        show_diff_dialog(item)
                                st.write("")
                else:
                    st.warning("Tidak ditemukan pola Bab atau Pasal yang dapat diekstraksi dari dokumen ini.")

            except Exception as e:
                st.error(f"Gagal memproses berkas: {str(e)}")
    else:
        render_html(
            """
            <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; padding: 24px; text-align: center; color: #64748b; font-size: 13px;">
                Silakan pilih berkas dokumen peraturan internal (.docx atau .pdf) pada kotak di atas untuk memulai ekstraksi otomatis.
            </div>
            """
        )


# TAB 3: Uji Klausul Mandiri
with tab_uji:
    st.markdown("#### Uji Mandiri Keselarasan Klausul Baru")
    st.markdown(
        "<span style='font-size: 13px; color: #475569;'>"
        "Gunakan modul ini untuk menguji keselarasan satu draf pasal operasional terhadap satu pasal regulasi pemerintah."
        "</span>",
        unsafe_allow_html=True,
    )

    col_in_1, col_in_2 = st.columns(2)
    with col_in_1:
        st.markdown("**1. Draf Teks Klausul Internal Bank (SOP / Petunjuk Operasional):**")
        custom_internal = st.text_area(
            "Teks Klausul Internal",
            value="Unit Kerja diperkenankan menyimpan salinan cadangan data nasabah pada penyedia komputasi awan pihak ketiga di kawasan Asia Tenggara tanpa persetujuan regulator.",
            height=130,
            label_visibility="collapsed",
        )
    with col_in_2:
        st.markdown("**2. Teks Regulasi Pemerintah / OJK (Pasal Acuan):**")
        custom_external = st.text_area(
            "Teks Regulasi Acuan",
            value="Bank wajib menempatkan data dan sistem di wilayah Indonesia. Penempatan di luar negeri wajib memperoleh persetujuan tertulis Otoritas Jasa Keuangan.",
            height=130,
            label_visibility="collapsed",
        )

    if st.button("Jalankan Uji Keselarasan", type="primary"):
        with st.spinner("Memproses evaluasi semantik dan pertimbangan hukum..."):
            eval_result = evaluate_custom_clause_alignment(custom_internal, custom_external)
            status = eval_result["status"]

            badge_styles = {
                "Tidak Selaras": ("#991b1b", "#fef2f2", "#fecaca"),
                "Selaras": ("#166534", "#f0fdf4", "#bbf7d0"),
                "Netral": ("#854d0e", "#fefce8", "#fef08a"),
            }
            c_txt, c_bg, c_bdr = badge_styles.get(status, ("#334155", "#f1f5f9", "#cbd5e1"))

            st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 16px 0;'>", unsafe_allow_html=True)
            st.markdown("##### Hasil Evaluasi Keselarasan")

            res_c1, res_c2 = st.columns([1, 2.5])
            with res_c1:
                render_html(
                    f"""
                    <div style="background-color: {c_bg}; border: 1px solid {c_bdr}; border-radius: 4px; padding: 16px; text-align: center;">
                        <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Status Evaluasi</div>
                        <div style="font-size: 20px; font-weight: 700; color: {c_txt}; margin: 6px 0;">{status.upper()}</div>
                        <div style="font-size: 11px; color: #64748b;">Keyakinan Model: {int(eval_result['confidence']*100)}%</div>
                    </div>
                    """
                )
            with res_c2:
                render_html(
                    f"""
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; padding: 14px;">
                        <div style="font-size: 12px; margin-bottom: 8px;"><strong>Pertimbangan Hukum:</strong> {eval_result['reasoning']}</div>
                        <div style="font-size: 12px; color: #475569;"><strong>Rekomendasi Revisi:</strong> {eval_result['rekomendasi']}</div>
                    </div>
                    """
                )

            st.markdown("##### Komparasi Redaksional (Diff)")
            diff_custom_html = render_side_by_side_diff_html(
                title_internal="Draf Klausul Internal yang Diuji",
                text_internal=custom_internal,
                title_regulasi="Regulasi Pemerintah Acuan",
                text_regulasi=custom_external,
                status=status,
                reasoning=eval_result["reasoning"],
            )
            render_html(diff_custom_html)


# TAB 4: Arsitektur & Panduan
with tab_panduan:
    st.markdown("#### Landasan Konsep & Arsitektur Sistem")
    st.markdown(
        """
        Sistem ini dibangun untuk mendemonstrasikan kelayakan otomatisasi pengujian kepatuhan regulasi di Bank Mandiri:

        1. **Permasalahan Kepatuhan**:
           Penerbitan POJK atau Surat Edaran baru membutuhkan telaah manual atas ratusan halaman SOP internal bank. Proses manual rentan terhadap kelelahan auditor dan risiko keterlambatan penyesuaian regulasi.

        2. **Prinsip Natural Language Inference (NLI)**:
           Evaluasi tidak menggunakan klasifikasi teks tunggal, melainkan pemetaan pasangan klausa (*premise* regulasi vs *hypothesis* SOP bank) untuk menentukan relasi *entailment* (selaras), *contradiction* (tidak selaras), atau *neutral* (netral).

        3. **Transparansi Hasil (Explainability)**:
           Setiap status dilengkapi dengan perbandingan redaksional kata-per-kata yang menyoroti deviasi spesifik, disertai pertimbangan hukum ringkas dan rekomendasi perbaikan pasal.

        4. **Keamanan Data Perbankan (Production Deployment)**:
           Untuk implementasi produksi, arsitektur ini dirancang untuk dijalankan secara *on-premise* menggunakan server privat internal Bank Mandiri, memastikan tidak ada dokumen rahasia bank yang keluar ke jaringan eksternal.
        """
    )
