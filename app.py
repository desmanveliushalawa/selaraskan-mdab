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
from engine.bucket_manager import (
    list_buckets,
    get_bucket,
    create_bucket,
    add_document_to_bucket,
    delete_bucket,
    get_bucket_retriever,
)


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
# Dokumentasi R-29 (Color Palette):
# - Core Primary: #003d79 (Navy Bank Mandiri) sebagai warna identitas institusional.
# - Semantic Success: #166534 / #f0fdf4 (Selaras)
# - Semantic Alert: #991b1b / #fef2f2 (Tidak Selaras / Risiko Deviasi)
# - Semantic Neutral: #854d0e / #fefce8 (Netral / Prosedural Teknis)
# - Slate Neutrals: #0f172a (teks utama), #475569 (kontras tinggi 7.24:1 untuk teks sekunder), #ffffff & #f8fafc (background).
# Dokumentasi R-31 (Border Radius):
# - 4px dipilih konsisten untuk seluruh elemen guna mempertahankan wibawa formal institusional perbankan.
render_html(
    """
    <script>document.documentElement.lang = "id";</script>
    <style>
    /* Tipografi Dasar */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
    }

    /* R-39: Affordance Kursor untuk seluruh kontrol interaktif */
    button, select, [role="button"], a {
        cursor: pointer !important;
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
        color: #475569; /* WCAG AA & AAA compliant 7.24:1 */
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
        color: #475569; /* WCAG AA compliant */
    }

    /* Kartu Klausul Hukum */
    .legal-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 12px;
        transition: border-color 0.15s ease;
    }
    .legal-card:hover {
        border-color: #003d79;
    }
    .legal-meta {
        font-size: 11px;
        font-weight: 600;
        color: #475569; /* WCAG AA compliant */
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

    /* Bucket Card (R-14: Hierarki Visual Tegas Antara Bawaan Sistem vs Kustom) */
    .bucket-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .bucket-card.bucket-default {
        border-left: 4px solid #003d79;
    }
    .bucket-card.bucket-custom {
        border-left: 4px solid #2563eb;
    }
    .bucket-card:hover {
        border-color: #003d79;
    }
    .badge-bucket-default {
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .badge-bucket-custom {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        font-size: 11px;
        font-weight: 600;
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
    if source_mode == "Contoh Studi Kasus (Bank Mandiri)":
        for reg in benchmark_data["external_benchmark"]["regulations"]:
            st.markdown(f"• <span style='font-size: 12px; color: #334155;'>{reg}</span>", unsafe_allow_html=True)
    elif "uploaded_analysis" in st.session_state:
        b_name = st.session_state["uploaded_analysis"].get("bucket_name", "Bucket Dokumen Acuan")
        st.markdown(f"<div style='font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase;'>Bucket Aktif:</div><div style='font-size: 12px; font-weight: 600; color: #003d79; margin-top: 2px;'>{b_name}</div>", unsafe_allow_html=True)
    else:
        st.caption("Pilih bucket acuan di Tab 'Unggah & Cek Keselarasan'.")

    st.markdown("---")
    st.markdown("### Filter Penelusuran")
    filter_status = st.selectbox(
        "Status Keselarasan:",
        options=["Semua Status", "Hanya Tidak Selaras (Prioritas Risiko)", "Hanya Selaras", "Hanya Netral"],
        index=0,
    )

    search_keyword = st.text_input("Pencarian Pasal atau Kata Kunci:", placeholder="Contoh: bunga, agunan, cloud...")

    st.markdown("---")
    st.markdown("### Ekspor Laporan")
    
    # Download button untuk mode saat ini
    if source_mode == "Contoh Studi Kasus (Bank Mandiri)":
        export_clauses = demo_clauses
        export_doc_info = demo_doc_info
        export_metrics = demo_metrics
        export_benchmark = benchmark_data["external_benchmark"]
    elif "uploaded_analysis" in st.session_state:
        export_clauses = st.session_state["uploaded_analysis"]["clauses"]
        export_doc_info = st.session_state["uploaded_analysis"]["doc_info"]
        export_metrics = st.session_state["uploaded_analysis"]["metrics"]
        export_benchmark = {
            "regulations": [st.session_state["uploaded_analysis"].get("bucket_name", "Bucket Dokumen Acuan")]
        }
    else:
        export_clauses = []
        export_doc_info = {"title": "Belum ada dokumen", "version": "v1.0", "subject": "-", "issued_date": "-"}
        export_metrics = calculate_compliance_metrics([])
        export_benchmark = {"regulations": ["-"]}

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
            data=generate_compliance_pdf_report(export_doc_info, export_benchmark, export_clauses, export_metrics),
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
current_bucket_label = "POJK, BI, UU PDP" if source_mode == "Contoh Studi Kasus (Bank Mandiri)" else (
    st.session_state["uploaded_analysis"].get("bucket_name", "Pilih di Tab Unggah") if "uploaded_analysis" in st.session_state else "Pilih di Tab Unggah"
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
                <div>Dokumen Target: <strong>{current_version}</strong></div>
                <div>Acuan: <strong>{current_bucket_label}</strong></div>
                <div>Mode: <strong>{'Contoh Demo' if source_mode == "Contoh Studi Kasus (Bank Mandiri)" else 'Audit Unggahan'}</strong></div>
            </div>
        </div>
    </div>
    """
)


# Tab Navigasi Utama (5 Tab Sesuai Kebutuhan Audit Fleksibel Multi-Tier)
tab_evaluasi, tab_unggah, tab_bucket, tab_uji, tab_panduan = st.tabs([
    "Matriks Keselarasan Dokumen",
    "Unggah & Cek Keselarasan",
    "Manajemen Bucket Dokumen Acuan",
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
        active_bucket_name = "Regulasi Acuan Eksternal (POJK 11/2022, UU PDP, BI)"
        st.info("Mode Pratinjau: Menampilkan contoh simulasi (Petunjuk Operasional No. PO-DIR/IT/042/2024 Bank Mandiri) terhadap Regulasi Acuan Eksternal. Untuk menguji dokumen lain atau mengganti bucket acuan, pilih 'Unggah Dokumen Baru' di sidebar kiri.")
    else:
        if "uploaded_analysis" in st.session_state:
            active_doc_info = st.session_state["uploaded_analysis"]["doc_info"]
            active_clauses = st.session_state["uploaded_analysis"]["clauses"]
            active_metrics = st.session_state["uploaded_analysis"]["metrics"]
            active_bucket_name = st.session_state["uploaded_analysis"].get("bucket_name", "Bucket Terpilih")
            st.success(f"Mode Dokumen Unggahan Aktif: Menampilkan hasil evaluasi dari berkas '{active_doc_info['title']}' terhadap Bucket Acuan '{active_bucket_name}'.")
        else:
            active_doc_info = None
            active_clauses = []
            active_metrics = None
            active_bucket_name = "Belum Dipilih"

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
                    <strong>Catatan Kepatuhan:</strong> Dari {active_metrics['total']} klausul yang dievaluasi terhadap <strong>{active_bucket_name}</strong>, terdeteksi {active_metrics['tidak_selaras']['count']} klausul yang memiliki deviasi normatif dan direkomendasikan untuk segera dilakukan addendum/penyesuaian kebijakan operasional.
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
                <p style="font-size: 13px; max-width: 580px; margin: 0 auto 16px auto; line-height: 1.5; color: #475569;">
                    Anda saat ini berada pada mode <strong>Unggah Dokumen Baru</strong>. Silakan buka tab <strong>"Unggah & Cek Keselarasan"</strong> di atas untuk mengunggah berkas Word (.docx) atau PDF regulasi Anda, atau alihkan pilihan ke <strong>"Contoh Studi Kasus (Bank Mandiri)"</strong> pada menu di sidebar kiri untuk melihat contoh simulasi.
                </p>
            </div>
            """
        )


# TAB 2: Unggah & Cek Keselarasan (Audit Dinamis Berbasis Bucket)
with tab_unggah:
    st.markdown("#### Unggah Dokumen Target & Uji Keselarasan Regulasi")
    st.markdown(
        "<span style='font-size: 13px; color: #475569;'>"
        "Pilih bucket regulasi acuan kepatuhan, tentukan dokumen operasional target yang ingin diuji, "
        "lalu klik tombol <strong>SUBMIT CEK KESELARASAN</strong> untuk menjalankan audit kepatuhan berbasis inferensi semantik."
        "</span>",
        unsafe_allow_html=True,
    )

    # 1. Pilih Bucket Dokumen Acuan (Rujukan Kepatuhan)
    st.markdown("##### 1. Pilih Bucket Dokumen Acuan (Rujukan Kepatuhan)")
    available_buckets = list_buckets()
    bucket_dict = {b["id"]: b for b in available_buckets}
    bucket_select_options = [b["id"] for b in available_buckets]

    selected_bucket_id = st.selectbox(
        "Pilih Bucket Dokumen Acuan:",
        options=bucket_select_options,
        format_func=lambda bid: f"{bucket_dict[bid]['name']} ({bucket_dict[bid]['category']} • {bucket_dict[bid]['total_clauses']} klausul)",
        index=0,
        help="Pilih repositori regulasi yang menjadi tolok ukur kepatuhan hukum untuk dokumen target yang akan diuji.",
    )

    sel_b = bucket_dict[selected_bucket_id]
    render_html(
        f"""
        <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #003d79; border-radius: 4px; padding: 10px 14px; margin: 8px 0 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase;">
                    Bucket Acuan Terpilih : {sel_b['category']}
                </div>
                <span class="{'badge-bucket-default' if sel_b.get('is_default') else 'badge-bucket-custom'}">
                    {'Bawaan Sistem' if sel_b.get('is_default') else 'Koleksi Kustom'}
                </span>
            </div>
            <div style="font-size: 13px; font-weight: 700; color: #003d79; margin: 2px 0 4px 0;">{sel_b['name']}</div>
            <div style="font-size: 12px; color: #334155; line-height: 1.4;">{sel_b['description']}</div>
            <div style="font-size: 11px; color: #475569; margin-top: 6px;">
                Total Dokumen Terindeks: <strong>{sel_b['total_files']}</strong> berkas • Total Klausul Norma: <strong>{sel_b['total_clauses']}</strong> klausul siap dicocokkan semantik
            </div>
        </div>
        """
    )

    # 2. Tentukan Dokumen Internal yang Ingin Diuji (Target)
    st.markdown("##### 2. Tentukan Dokumen Internal yang Ingin Diuji (Target)")
    st.caption("Gunakan salah satu tombol cepat untuk memuat berkas kebijakan Bank Mandiri siap uji, atau unggah dokumen internal Anda sendiri:")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        if st.button("Uji SOP KUR Mandiri", key="btn_sample_sop_kur", use_container_width=True):
            st.session_state["target_file_path"] = "dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.pdf"
            st.session_state["target_file_label"] = "SOP_Penyaluran_KUR_Bank_Mandiri.pdf"
            st.rerun()
    with col_s2:
        if st.button("Uji RIPLAY KUR Mandiri", key="btn_sample_riplay_kur", use_container_width=True):
            st.session_state["target_file_path"] = "dokumen_internal_mandiri/RIPLAY_Ketentuan_KUR_Bank_Mandiri.pdf"
            st.session_state["target_file_label"] = "RIPLAY_Ketentuan_KUR_Bank_Mandiri.pdf"
            st.rerun()
    with col_s3:
        if st.button("Uji Kebijakan Kredit KPKD", key="btn_sample_kpkd", use_container_width=True):
            st.session_state["target_file_path"] = "data/Kebijakan Perkreditan i3655.pdf"
            st.session_state["target_file_label"] = "Kebijakan_Perkreditan_Bank_Mandiri.pdf"
            st.rerun()
    with col_s4:
        if st.button("Uji Kebijakan TI Siber", key="btn_sample_cyber", use_container_width=True):
            st.session_state["target_file_path"] = "data/sample_kebijakan_internal_mandiri.pdf"
            st.session_state["target_file_label"] = "Kebijakan_TI_Siber_Mandiri.pdf"
            st.rerun()

    uploaded_file = st.file_uploader(
        "Atau unggah berkas dokumen peraturan internal (.docx, .pdf, .txt):",
        type=["docx", "pdf", "txt"],
        help="Mendukung dokumen Microsoft Word (.docx), PDF standar (.pdf), atau teks mentah (.txt)",
        key="target_file_uploader",
    )

    # Unduh Berkas Contoh (Jika ingin download manual)
    with st.expander("Unduh Berkas Kebijakan Bank Mandiri untuk Pengujian Manual", expanded=False):
        col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
        kur_pdf = "dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.pdf"
        kur_docx = "dokumen_internal_mandiri/SOP_Penyaluran_KUR_Bank_Mandiri.docx"
        riplay_pdf = "dokumen_internal_mandiri/RIPLAY_Ketentuan_KUR_Bank_Mandiri.pdf"
        kpkd_pdf = "data/Kebijakan Perkreditan i3655.pdf"
        with col_dl1:
            if os.path.exists(kur_pdf):
                with open(kur_pdf, "rb") as f:
                    st.download_button("SOP KUR (PDF)", data=f.read(), file_name="SOP_Penyaluran_KUR_Bank_Mandiri.pdf", mime="application/pdf", use_container_width=True)
        with col_dl2:
            if os.path.exists(kur_docx):
                with open(kur_docx, "rb") as f:
                    st.download_button("SOP KUR (DOCX)", data=f.read(), file_name="SOP_Penyaluran_KUR_Bank_Mandiri.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with col_dl3:
            if os.path.exists(riplay_pdf):
                with open(riplay_pdf, "rb") as f:
                    st.download_button("RIPLAY KUR (PDF)", data=f.read(), file_name="RIPLAY_Ketentuan_KUR_Bank_Mandiri.pdf", mime="application/pdf", use_container_width=True)
        with col_dl4:
            if os.path.exists(kpkd_pdf):
                with open(kpkd_pdf, "rb") as f:
                    st.download_button("KPKD Mandiri (PDF)", data=f.read(), file_name="Kebijakan_Perkreditan_Bank_Mandiri.pdf", mime="application/pdf", use_container_width=True)

    # Tentukan sumber berkas target (dari upload langsung atau dari tombol cepat)
    target_bytes = None
    target_filename = None

    if uploaded_file is not None:
        target_bytes = uploaded_file.getvalue() # Menggunakan getvalue() agar pointer buffer tidak hilang saat rerun
        target_filename = uploaded_file.name
    elif "target_file_path" in st.session_state and os.path.exists(st.session_state["target_file_path"]):
        with open(st.session_state["target_file_path"], "rb") as f:
            target_bytes = f.read()
        target_filename = st.session_state["target_file_label"]

    if target_bytes is not None and target_filename is not None:
        file_size_kb = round(len(target_bytes) / 1024, 1)

        # Caching ekstraksi parsing di session state agar tidak re-parse berulang saat klik tombol dialog/filter
        cache_key = f"parsed_{target_filename}_{len(target_bytes)}"
        if "parsed_cache" not in st.session_state:
            st.session_state["parsed_cache"] = {}

        if cache_key in st.session_state["parsed_cache"]:
            parsed_doc = st.session_state["parsed_cache"][cache_key]
        else:
            with st.spinner(f"Mengekstrak struktur Bab & Pasal dari '{target_filename}'..."):
                try:
                    raw_text = extract_raw_text(target_bytes, target_filename)
                    parsed_doc = parse_legal_structure(raw_text)
                    st.session_state["parsed_cache"][cache_key] = parsed_doc
                except Exception as e:
                    st.error(f"Gagal memproses berkas target: {str(e)}")
                    parsed_doc = None

        if parsed_doc:
            render_html(
                f"""
                <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; padding: 10px 14px; margin: 12px 0; font-size: 13px; color: #166534;">
                    Dokumen Target <strong>'{target_filename}'</strong> berhasil diekstrak. Terdeteksi {parsed_doc['total_bab']} Bab, {parsed_doc['total_pasal']} Pasal/Artikel, dan {parsed_doc['total_ayat']} Ayat/Butir.
                </div>
                """
            )

            # Metadata Cards
            meta_cols = st.columns(4)
            with meta_cols[0]:
                render_html(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Nama Berkas Target</div>
                        <div style="font-size: 13px; font-weight: 600; color: #003d79; margin: 4px 0;">{target_filename[:24]}</div>
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
                        <div class="metric-label">Total Pasal / Artikel</div>
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

            # Tabel Klausul yang Terdaftar
            st.markdown("##### Rincian Klausul yang Terdaftar pada Dokumen Target")
            if parsed_doc["clauses"]:
                display_parsed_clauses = filter_clause_list(parsed_doc["clauses"], "Semua Status", search_keyword)
                if search_keyword.strip():
                    st.caption(f"Menampilkan {len(display_parsed_clauses)} dari {len(parsed_doc['clauses'])} klausul untuk kata kunci: \"{search_keyword.strip()}\"")

                df_parsed = pd.DataFrame([
                    {
                        "No": i + 1,
                        "Bab": c["bab"],
                        "Pasal / Artikel": c["pasal"],
                        "Ayat / Butir": c["ayat"],
                        "Teks Klausul": (c["text"][:110] + "...") if len(c["text"]) > 110 else c["text"],
                    }
                    for i, c in enumerate(display_parsed_clauses)
                ])
                st.dataframe(df_parsed, use_container_width=True, hide_index=True)

                # Tombol Utama: SUBMIT CEK KESELARASAN
                st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 16px 0;'>", unsafe_allow_html=True)
                st.markdown("##### 3. Eksekusi Pengujian Kepatuhan")
                st.write(f"Audit keselarasan akan memetakan seluruh klausul dari **{target_filename}** terhadap norma acuan di **{sel_b['name']}**.")

                if st.button("SUBMIT CEK KESELARASAN", type="primary", use_container_width=True):
                    with st.spinner(f"Mencocokkan {len(parsed_doc['clauses'])} klausul dengan Bucket '{sel_b['name']}' menggunakan Semantic Retriever..."):
                        retriever = get_bucket_retriever(selected_bucket_id)
                        eval_list = []
                        # R-31 & Karpathy K-4: Ambang batas kecocokan semantik (Semantic Similarity Threshold).
                        # Nilai 0.10 dipilih sebagai baseline minimum untuk menyaring pasangan dokumen yang tidak berkorelasi.
                        SEMANTIC_MATCH_THRESHOLD = 0.10
                        for i, c in enumerate(parsed_doc["clauses"]):
                            matches = retriever.retrieve_best_match(c["text"], top_k=1)
                            if matches and matches[0]["similarity_score"] >= SEMANTIC_MATCH_THRESHOLD:
                                ref_sample = matches[0]
                                sim_pct = int(ref_sample["similarity_score"] * 100)
                            else:
                                # Fallback normatif umum: Jika tidak ada klausul spesifik yang cocok langsung,
                                # klausul dievaluasi terhadap prinsip umum kepatuhan dan kehati-hatian perbankan.
                                ref_sample = {
                                    "regulasi_terkait": sel_b["name"],
                                    "pasal_regulasi": "Ketentuan Umum Asas Kepatuhan",
                                    "teks_regulasi": "Ketentuan teknis operasional perbankan harus tunduk pada asas kehati-hatian, kepatuhan regulasi, dan mitigasi risiko.",
                                }
                                sim_pct = 0

                            eval_res = evaluate_custom_clause_alignment(c["text"], ref_sample["teks_regulasi"])
                            eval_list.append({
                                "id": f"UP-{i+1:03d}",
                                "bab": c["bab"],
                                "pasal": c["pasal"],
                                "ayat": c["ayat"],
                                "judul_klausul": f"{c['pasal']} {c['ayat']}",
                                "teks_internal": c["text"],
                                "regulasi_terkait": ref_sample.get("regulasi_terkait", sel_b["name"]),
                                "pasal_regulasi": ref_sample.get("pasal_regulasi", "-"),
                                "teks_regulasi": ref_sample.get("teks_regulasi", ""),
                                "similarity_pct": sim_pct,
                                "status": eval_res["status"],
                                "reasoning": eval_res["reasoning"],
                                "rekomendasi": eval_res["rekomendasi"],
                            })

                        up_metrics = calculate_compliance_metrics(eval_list)
                        
                        # Simpan ke session state agar persisten dan Tab 1 otomatis sinkron
                        st.session_state["uploaded_analysis"] = {
                            "filename": target_filename,
                            "bucket_id": selected_bucket_id,
                            "bucket_name": sel_b["name"],
                            "doc_info": {
                                "title": parsed_doc["title"],
                                "subject": f"Ekstraksi dari berkas {target_filename}",
                                "version": f"v1.0 ({target_filename[:20]})",
                                "issued_date": "Terbaru",
                            },
                            "clauses": eval_list,
                            "metrics": up_metrics,
                        }
                        st.rerun()

                    # Render hasil evaluasi dari session state (persisten saat tombol dialog diklik)
                    if (
                        "uploaded_analysis" in st.session_state
                        and st.session_state["uploaded_analysis"].get("filename") == target_filename
                    ):
                        analysis = st.session_state["uploaded_analysis"]
                        saved_metrics = analysis["metrics"]
                        saved_clauses = analysis["clauses"]

                        display_eval_clauses = filter_clause_list(saved_clauses, filter_status, search_keyword)

                        st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
                        st.markdown("##### Hasil Evaluasi Keselarasan terhadap Bucket Acuan")

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
                                        <strong>Ketentuan Acuan ({sel_b['name']}):</strong> {item['regulasi_terkait']} ({item['pasal_regulasi']}) • 
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
                    st.warning("Tidak ditemukan pola Bab atau Pasal yang dapat diekstraksi dari dokumen target ini.")
    else:
        render_html(
            """
            <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; padding: 24px; text-align: center; color: #475569; font-size: 13px;">
                Silakan pilih salah satu tombol cepat contoh berkas di atas atau unggah dokumen peraturan internal (.docx atau .pdf) untuk memulai ekstraksi dan audit keselarasan.
            </div>
            """
        )


# TAB 3: Manajemen Bucket Dokumen Acuan (Knowledge Base Management)
with tab_bucket:
    st.markdown("#### Manajemen Bucket Dokumen Acuan (Knowledge Base Management)")
    st.markdown(
        "<span style='font-size: 13px; color: #475569;'>"
        "Modul manajemen repositori regulasi dan kebijakan rujukan. Pengguna dapat membuat bucket acuan baru, "
        "mengunggah berkas peraturan resmi (.pdf / .docx), dan mengelola koleksi norma kepatuhan secara dinamis."
        "</span>",
        unsafe_allow_html=True,
    )
    
    # Metrik Utama Pengetahuan Kepatuhan
    all_buckets = list_buckets()
    total_buckets = len(all_buckets)
    total_files_indexed = sum(b.get("total_files", 0) for b in all_buckets)
    total_clauses_indexed = sum(b.get("total_clauses", 0) for b in all_buckets)

    bm1, bm2, bm3 = st.columns(3)
    with bm1:
        render_html(f"""
        <div class="metric-box">
            <div class="metric-label">Total Bucket Dokumen</div>
            <div class="metric-number" style="color: #003d79;">{total_buckets}</div>
            <div class="metric-desc">Koleksi Pengetahuan Kepatuhan</div>
        </div>
        """)
    with bm2:
        render_html(f"""
        <div class="metric-box">
            <div class="metric-label">Total Berkas Terindeks</div>
            <div class="metric-number" style="color: #003d79;">{total_files_indexed}</div>
            <div class="metric-desc">Dokumen Peraturan / Kebijakan</div>
        </div>
        """)
    with bm3:
        render_html(f"""
        <div class="metric-box">
            <div class="metric-label">Total Klausul Norma Acuan</div>
            <div class="metric-number" style="color: #166534;">{total_clauses_indexed}</div>
            <div class="metric-desc">Klausul Siap Dicocokkan Semantik</div>
        </div>
        """)

    # Multi-tier explanation callout
    render_html("""
    <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px; padding: 12px 16px; margin: 16px 0;">
        <div style="font-size: 12px; font-weight: 700; color: #003d79; margin-bottom: 4px;">Arsitektur Audit Kepatuhan Multi-Tier Perbankan:</div>
        <div style="font-size: 12px; color: #334155; line-height: 1.5;">
            <strong>Kasus 1:</strong> Dokumen internal operasional (Juknis/SOP) diuji keselarasan terhadap <em>Bucket Kebijakan Internal Perkreditan Bank Mandiri (KPKD)</em>.<br/>
            <strong>Kasus 2:</strong> Dokumen Kebijakan Perkreditan Bank Mandiri diuji keselarasan terhadap <em>Bucket Regulasi Eksternal Pemerintah, OJK, dan Bank Indonesia</em>.
        </div>
    </div>
    """)

    st.markdown("##### Koleksi Bucket yang Tersedia")
    for b in all_buckets:
        full_b = get_bucket(b["id"]) or b
        # R-09: Badge fungsional membedakan korpus regulasi bawaan sistem (tidak dapat dihapus) vs koleksi kustom pengguna (dapat dihapus)
        is_default = b.get("is_default", False)
        badge_type = "Bawaan Sistem" if is_default else "Koleksi Pengguna"
        badge_style = "background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1;" if is_default else "background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe;"
        card_class = "bucket-card bucket-default" if is_default else "bucket-card bucket-custom"

        render_html(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: #475569;">{b.get('category', 'Kustom')}</span>
                    <h4 style="margin: 2px 0 6px 0; color: #003d79; font-size: 15px;">{b['name']}</h4>
                </div>
                <span style="font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; {badge_style}">{badge_type}</span>
            </div>
            <div style="font-size: 12px; color: #334155; line-height: 1.4; margin-bottom: 8px;">{b.get('description', '')}</div>
            <div style="font-size: 11px; color: #475569;">
                ID: <code>{b['id']}</code> • <strong>{b.get('total_files', 0)}</strong> Berkas Fisik • <strong>{b.get('total_clauses', 0)}</strong> Klausul Terindeks
            </div>
        </div>
        """)

        with st.expander(f"Lihat Berkas & Sampel Klausul: {b['name']}", expanded=False):
            col_f, col_c = st.columns([1, 2])
            with col_f:
                st.markdown("**Daftar Berkas Terdaftar:**")
                files = full_b.get("files", [])
                if files:
                    for fn in files:
                        st.markdown(f"• `{fn}`")
                else:
                    st.caption("Belum ada berkas fisik yang disimpan.")
            with col_c:
                st.markdown("**Sampel Klausul Terindeks (Maks. 5):**")
                clauses_sample = full_b.get("clauses", [])[:5]
                if clauses_sample:
                    df_sample = pd.DataFrame([
                        {
                            "ID": cs.get("id", "-"),
                            "Pasal / Topik": cs.get("pasal_regulasi", cs.get("topik", "-")),
                            "Teks Acuan": (cs.get("teks_regulasi", "")[:85] + "...") if len(cs.get("teks_regulasi", "")) > 85 else cs.get("teks_regulasi", ""),
                        }
                        for cs in clauses_sample
                    ])
                    st.dataframe(df_sample, use_container_width=True, hide_index=True)
                else:
                    st.caption("Belum ada klausul terindeks.")

            if not is_default:
                if st.button(f"Hapus Bucket '{b['name']}'", key=f"del_bucket_{b['id']}"):
                    try:
                        delete_bucket(b["id"])
                        st.success(f"Bucket '{b['name']}' berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus bucket: {str(e)}")

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;'>", unsafe_allow_html=True)

    # Dua Form Penambahan
    col_add_doc, col_new_bucket = st.columns(2)

    with col_add_doc:
        st.markdown("##### A. Tambah Berkas Baru ke Bucket Acuan")
        st.caption("Unggah berkas peraturan atau kebijakan untuk mengekstrak klausul dan menambahkannya ke bucket yang sudah ada.")
        
        target_b_id = st.selectbox(
            "Pilih Bucket Tujuan:",
            options=[b["id"] for b in all_buckets],
            format_func=lambda bid: next(b["name"] for b in all_buckets if b["id"] == bid),
            key="add_doc_bucket_select",
        )
        add_file = st.file_uploader(
            "Unggah Berkas Acuan (.pdf, .docx, .txt):",
            type=["pdf", "docx", "txt"],
            key="add_doc_file_uploader",
        )
        if st.button("Ekstrak & Tambahkan ke Bucket", type="primary", key="btn_add_doc_to_bucket"):
            if add_file is not None:
                with st.spinner("Mengekstrak teks dan mengindeks klausul ke bucket..."):
                    try:
                        bytes_data = add_file.getvalue()
                        res = add_document_to_bucket(target_b_id, bytes_data, add_file.name)
                        st.success(f"Berhasil menambahkan '{add_file.name}'! Terindeks {res['new_clauses_count']} klausul baru. Total klausul di bucket: {res['total_clauses_count']}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan dokumen ke bucket: {str(e)}")
            else:
                st.warning("Pilih berkas terlebih dahulu sebelum menekan tombol.")

    with col_new_bucket:
        st.markdown("##### B. Buat Bucket Dokumen Acuan Baru")
        st.caption("Buat kategori bucket acuan baru untuk memisahkan domain kepatuhan (misal: Unit Anti-Pencucian Uang, Audit TI, Manajemen Risiko).")

        new_b_name = st.text_input("Nama Bucket Baru:", placeholder="Contoh: Ketentuan Manajemen Risiko Likuiditas 2024", key="input_new_b_name")
        new_b_cat = st.selectbox(
            "Kategori Dokumen:",
            options=["Kebijakan Internal Tier-1", "Regulasi Eksternal (Regulator)", "Petunjuk Teknis Lapangan (Tier-2 SOP)", "Standar Audit & Kepatuhan", "Koleksi Kustom Divisi"],
            key="select_new_b_cat",
        )
        new_b_desc = st.text_area("Deskripsi Singkat:", placeholder="Jelaskan cakupan dokumen acuan di dalam bucket ini...", height=85, key="input_new_b_desc")
        
        if st.button("Buat Bucket Baru", type="primary", key="btn_create_bucket"):
            if new_b_name.strip():
                try:
                    created = create_bucket(new_b_name.strip(), new_b_desc.strip(), new_b_cat)
                    st.success(f"Bucket '{created['name']}' berhasil dibuat! Anda kini dapat menambahkan berkas dokumen ke dalamnya.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal membuat bucket baru: {str(e)}")
            else:
                st.warning("Nama bucket wajib diisi.")


# TAB 4: Uji Klausul Mandiri
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


# TAB 5: Arsitektur & Konsep Sistem
with tab_panduan:
    st.markdown("#### Landasan Konsep & Arsitektur Sistem")
    st.markdown(
        """
        Sistem ini dibangun untuk mendemonstrasikan kelayakan otomatisasi pengujian kepatuhan regulasi di Bank Mandiri:

        1. **Arsitektur Knowledge Base Multi-Bucket**:
           Kepatuhan hukum perbankan tidak bersifat satu dimensi. Sistem mendukung audit bertingkat (*multi-tier compliance*):
           - Petunjuk Teknis / SOP Lapangan diaudit terhadap Kebijakan Induk Perkreditan Bank Mandiri (KPKD).
           - Kebijakan Induk Bank Mandiri diaudit terhadap Regulasi Nasional (POJK, Bank Indonesia, UU PDP).
           - Pengguna dapat membuat bucket acuan baru dan mengunggah dokumen regulasi secara fleksibel tanpa keterikatan pada database statis.

        2. **Prinsip Natural Language Inference (NLI)**:
           Evaluasi tidak menggunakan klasifikasi teks tunggal, melainkan pemetaan pasangan klausa (*premise* regulasi vs *hypothesis* SOP bank) untuk menentukan relasi *entailment* (selaras), *contradiction* (tidak selaras), atau *neutral* (netral).

        3. **Transparansi Hasil (Explainability)**:
           Setiap status dilengkapi dengan perbandingan redaksional kata-per-kata yang menyoroti deviasi spesifik, disertai pertimbangan hukum ringkas dan rekomendasi perbaikan pasal.

        4. **Keamanan Data Perbankan (Production Deployment)**:
           Untuk implementasi produksi, arsitektur ini dirancang untuk dijalankan secara *on-premise* menggunakan server privat internal Bank Mandiri, memastikan tidak ada dokumen rahasia bank yang keluar ke jaringan eksternal.
        """
    )
