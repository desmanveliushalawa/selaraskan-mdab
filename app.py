"""
app.py
Aplikasi Prototipe Streamlit: Mandiri RegAlign
Uji Keselarasan Regulasi Operasional Bank Mandiri vs Peraturan Pemerintah (POJK, BI, UU PDP)
Terinspirasi dari antarmuka Big Legal by BigBox (Telkom Indonesia).
"""

import io
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.diff_highlighter import render_side_by_side_diff_html
from engine.alignment_engine import (
    load_benchmark_data,
    calculate_compliance_metrics,
    evaluate_custom_clause_alignment,
)

# ---------------------------------------------------------
# 1. Konfigurasi Halaman & Tema
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mandiri RegAlign - Uji Keselarasan Regulasi",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Mandiri Blue #003d79, Gold #f5a623, Clean White Cards)
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #003d79 0%, #002244 100%);
        padding: 22px 28px;
        border-radius: 10px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 12px rgba(0, 61, 121, 0.15);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #e2e8f0;
        font-size: 14px;
        margin: 6px 0 0 0;
    }
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-title {
        font-size: 12px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 800;
        margin: 4px 0;
    }
    .status-badge-selaras {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #a5d6a7;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    .status-badge-tidaksaras {
        background-color: #ffebee;
        color: #c62828;
        border: 1px solid #ef9a9a;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    .status-badge-netral {
        background-color: #fffde7;
        color: #f57f17;
        border: 1px solid #fff59d;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    .clause-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s ease-in-out;
    }
    .clause-card:hover {
        border-color: #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 2. Fungsi Modal Pop-up Before-After Diff (@st.dialog)
# ---------------------------------------------------------
@st.dialog("⚖️ Detail Komparasi Redaksional (Before-After)", width="large")
def show_diff_dialog(clause: dict):
    """Menampilkan modal dialog perbandingan kalimat sebelum dan sesudah."""
    st.caption(f"ID Klausul: **{clause.get('id', '')}** — {clause.get('judul_klausul', '')}")
    
    diff_html = render_side_by_side_diff_html(
        title_internal=f"{clause.get('bab', '')} • {clause.get('pasal', '')}",
        text_internal=clause.get("teks_internal", ""),
        title_regulasi=f"{clause.get('regulasi_terkait', '')} • {clause.get('pasal_regulasi', '')}",
        text_regulasi=clause.get("teks_regulasi", ""),
        status=clause.get("status", "Netral"),
        reasoning=clause.get("reasoning", ""),
    )
    st.markdown(diff_html, unsafe_allow_html=True)
    
    rekomendasi = clause.get("rekomendasi", "")
    if rekomendasi:
        st.info(f"💡 **Rekomendasi Tindakan Kepatuhan:** {rekomendasi}")
        
    if st.button("Tutup Dialog", use_container_width=True):
        st.rerun()


# ---------------------------------------------------------
# 3. Muat Data & Inisialisasi State
# ---------------------------------------------------------
@st.cache_data
def get_cached_data():
    return load_benchmark_data()

benchmark_data = get_cached_data()
doc_info = benchmark_data["internal_document"]
clauses = benchmark_data["clauses"]
metrics = calculate_compliance_metrics(clauses)


# ---------------------------------------------------------
# 4. Header Utama
# ---------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>🏛️ Mandiri RegAlign</h1>
                <p>Sistem Uji Keselarasan Regulasi Perbankan (Petunjuk Operasional Bank Mandiri vs Peraturan Pemerintah)</p>
            </div>
            <div style="text-align: right; background: rgba(255,255,255,0.12); padding: 8px 16px; border-radius: 6px;">
                <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Referensi Desain:</span><br>
                <strong style="color: #f5a623; font-size: 13px;">Big Legal by BigBox (Telkom)</strong>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 5. Sidebar: Info Dokumen & Filter
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/ad/Bank_Mandiri_logo_2016.svg", width=180)
    st.markdown("---")
    
    st.subheader("📄 Dokumen Dievaluasi")
    st.markdown(f"**{doc_info['title']}**")
    st.caption(f"Perihal: {doc_info['subject']}")
    st.caption(f"Versi: `{doc_info['version']}` • Tanggal: {doc_info['issued_date']}")
    
    st.markdown("---")
    st.subheader("⚖️ Regulasi Pembanding")
    for reg in benchmark_data["external_benchmark"]["regulations"]:
        st.markdown(f"• <span style='font-size: 12px;'>{reg}</span>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("🔍 Filter Tampilan")
    filter_status = st.selectbox(
        "Filter Status Keselarasan:",
        options=["Semua Status", "Hanya Tidak Selaras (Prioritas Risiko)", "Hanya Selaras", "Hanya Netral"],
        index=0,
    )
    
    search_keyword = st.text_input("Cari Kata Kunci / Pasal:", placeholder="misal: enkripsi, drc, cloud...")
    
    st.markdown("---")
    # Tombol Ekspor CSV
    df_export = pd.DataFrame([
        {
            "ID": c["id"],
            "Bab": c["bab"],
            "Pasal Internal": c["pasal"],
            "Judul": c["judul_klausul"],
            "Status": c["status"],
            "Regulasi Terkait": c["regulasi_terkait"],
            "Pasal Regulasi": c["pasal_regulasi"],
            "Reasoning": c["reasoning"],
            "Rekomendasi": c["rekomendasi"],
        }
        for c in clauses
    ])
    csv_buffer = io.StringIO()
    df_export.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Laporan Audit (CSV)",
        data=csv_buffer.getvalue(),
        file_name="Laporan_Keselarasan_Regulasi_Bank_Mandiri.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ---------------------------------------------------------
# 6. Ringkasan Eksekutif & Donut Chart
# ---------------------------------------------------------
col_kpi, col_chart = st.columns([1.6, 1.2])

with col_kpi:
    st.markdown("### 📊 Ringkasan Kepatuhan Regulasi")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Klausul</div>
                <div class="metric-value" style="color: #003d79;">{metrics['total']}</div>
                <span style="font-size: 11px; color: #888;">Dokumen PO</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Selaras</div>
                <div class="metric-value" style="color: #2e7d32;">{metrics['selaras']['count']}</div>
                <span style="font-size: 11px; color: #2e7d32; font-weight: 600;">{metrics['selaras']['pct']}% Sesuai</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 3px solid #c62828;">
                <div class="metric-title">Tidak Selaras</div>
                <div class="metric-value" style="color: #c62828;">{metrics['tidak_selaras']['count']}</div>
                <span style="font-size: 11px; color: #c62828; font-weight: 700;">{metrics['tidak_selaras']['pct']}% Risiko</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Netral</div>
                <div class="metric-value" style="color: #f57f17;">{metrics['netral']['count']}</div>
                <span style="font-size: 11px; color: #f57f17; font-weight: 600;">{metrics['netral']['pct']}% Operasional</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 6px; padding: 10px 14px; margin-top: 14px; font-size: 12px; color: #475569;">
            💡 <strong>Executive Takeaway:</strong> Terdapat <strong>2 klausul berisiko ketidakselarasan tinggi</strong> terkait batas waktu laporan kebocoran data (UU PDP) dan penempatan server Cloud di luar negeri (POJK 11/2022). Direkomendasikan revisi redaksional segera.
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_chart:
    # Donut Chart Plotly sesuai Gambar 1 Big Legal (Pos: Hijau, Neg: Merah, Net: Kuning)
    labels = ["Selaras (Positif)", "Tidak Selaras (Negatif)", "Netral"]
    values = [metrics["selaras"]["count"], metrics["tidak_selaras"]["count"], metrics["netral"]["count"]]
    colors = ["#2e7d32", "#c62828", "#fbc02d"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors),
        textinfo="percent+value",
        hoverinfo="label+value+percent",
        textfont_size=12,
    )])
    fig.update_layout(
        showlegend=True,
        height=210,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# ---------------------------------------------------------
# 7. Tab Utama Aplikasi
# ---------------------------------------------------------
tab_dashboard, tab_custom, tab_about = st.tabs([
    "📑 Matriks Keselarasan Dokumen (Big Legal View)",
    "🧪 Uji Klausul Kustom (Live Testing)",
    "ℹ️ Panduan Presentasi & Arsitektur",
])


# ---------------------------------------------------------
# TAB 1: Matriks Keselarasan Dokumen (Big Legal View)
# ---------------------------------------------------------
with tab_dashboard:
    # Filter Klausul
    filtered_clauses = clauses
    if filter_status == "Hanya Tidak Selaras (Prioritas Risiko)":
        filtered_clauses = [c for c in filtered_clauses if c["status"] == "Tidak Selaras"]
    elif filter_status == "Hanya Selaras":
        filtered_clauses = [c for c in filtered_clauses if c["status"] == "Selaras"]
    elif filter_status == "Hanya Netral":
        filtered_clauses = [c for c in filtered_clauses if c["status"] == "Netral"]
        
    if search_keyword.strip():
        kw = search_keyword.strip().lower()
        filtered_clauses = [
            c for c in filtered_clauses
            if kw in c["judul_klausul"].lower()
            or kw in c["teks_internal"].lower()
            or kw in c["regulasi_terkait"].lower()
            or kw in c["pasal"].lower()
        ]

    # Layout 2 Kolom ala Big Legal
    col_left, col_right = st.columns([1.1, 1.9])

    with col_left:
        st.markdown("#### 📂 Hirarki Dokumen Internal")
        st.caption("Klik klausul di sebelah kanan untuk melihat komparasi detail.")
        
        # Kelompokkan berdasarkan Bab
        babs = {}
        for c in clauses:
            babs.setdefault(c["bab"], []).append(c)
            
        for bab_name, items in babs.items():
            with st.expander(f"📁 {bab_name}", expanded=True):
                for item in items:
                    badge_icon = "🟢" if item["status"] == "Selaras" else ("🔴" if item["status"] == "Tidak Selaras" else "🟡")
                    st.markdown(
                        f"""
                        <div style="font-size: 12px; margin-bottom: 8px; padding-left: 6px; border-left: 2px solid #cbd5e1;">
                            <strong>{item['pasal']}</strong>: {item['judul_klausul']}<br>
                            <span style="font-size: 11px;">Status: {badge_icon} <em>{item['status']}</em></span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with col_right:
        st.markdown(f"#### ⚖️ Hasil Evaluasi Keselarasan ({len(filtered_clauses)} Klausul)")
        
        if not filtered_clauses:
            st.warning("Tidak ditemukan klausul yang cocok dengan filter pencarian.")
        else:
            for idx, clause in enumerate(filtered_clauses):
                status = clause["status"]
                badge_class = (
                    "status-badge-selaras" if status == "Selaras"
                    else ("status-badge-tidaksaras" if status == "Tidak Selaras" else "status-badge-netral")
                )
                
                with st.container():
                    st.markdown(
                        f"""
                        <div class="clause-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                                <div>
                                    <span style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">
                                        {clause['id']} • {clause['bab']}
                                    </span>
                                    <h4 style="margin: 3px 0 0 0; color: #003d79; font-size: 15px;">
                                        {clause['pasal']}: {clause['judul_klausul']}
                                    </h4>
                                </div>
                                <span class="{badge_class}">{status.upper()}</span>
                            </div>
                            
                            <div style="background: #f8fafc; padding: 10px 12px; border-radius: 6px; font-size: 12px; margin-bottom: 10px; border-left: 3px solid #94a3b8;">
                                <strong>Rujukan Regulasi:</strong> {clause['regulasi_terkait']} — <em>{clause['pasal_regulasi']}</em>
                            </div>
                            
                            <div style="font-size: 12px; color: #334155; margin-bottom: 12px; line-height: 1.5;">
                                <strong>📌 Pertimbangan Hukum (Reasoning):</strong> {clause['reasoning']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # Tombol interaktif untuk memunculkan Before-After modal
                    btn_col1, btn_col2 = st.columns([1.5, 3])
                    with btn_col1:
                        if st.button(
                            f"🔍 Lihat Perbandingan (Before-After)",
                            key=f"btn_diff_{clause['id']}_{idx}",
                            use_container_width=True,
                        ):
                            show_diff_dialog(clause)
                    
                    st.write("")  # Spacing


# ---------------------------------------------------------
# TAB 2: Uji Klausul Kustom (Live Interactive Testing)
# ---------------------------------------------------------
with tab_custom:
    st.markdown("### 🧪 Uji Keselarasan Klausul Baru Secara Mandiri")
    st.write(
        "Gunakan formulir ini untuk menguji secara dinamis pasangan klausul operasional internal bank "
        "dengan pasal peraturan kementerian/OJK baru."
    )
    
    col_in_a, col_in_b = st.columns(2)
    with col_in_a:
        st.markdown("**1. Teks Klausul Petunjuk Operasional (Internal Bank):**")
        custom_internal = st.text_area(
            "Klausul Internal:",
            value="Unit Kerja diperkenankan menyimpan salinan cadangan data nasabah pada server cloud penyedia pihak ketiga di kawasan Asia Tenggara tanpa persetujuan regulator.",
            height=130,
            label_visibility="collapsed",
        )
    with col_in_b:
        st.markdown("**2. Teks Regulasi Pemerintah / OJK (Acuan Kepatuhan):**")
        custom_external = st.text_area(
            "Regulasi Acuan:",
            value="Bank wajib menempatkan data dan sistem di wilayah Indonesia. Penempatan di luar negeri wajib memperoleh persetujuan tertulis Otoritas Jasa Keuangan.",
            height=130,
            label_visibility="collapsed",
        )
        
    if st.button("🚀 Jalankan Evaluasi Keselarasan", type="primary"):
        with st.spinner("Menganalisis keselarasan semantik & pertimbangan hukum..."):
            eval_result = evaluate_custom_clause_alignment(custom_internal, custom_external)
            
            status = eval_result["status"]
            badge_color = "#2e7d32" if status == "Selaras" else ("#c62828" if status == "Tidak Selaras" else "#f57f17")
            
            st.markdown("---")
            st.markdown("#### 🎯 Hasil Evaluasi AI:")
            
            res_c1, res_c2 = st.columns([1, 2.5])
            with res_c1:
                st.markdown(
                    f"""
                    <div style="background: white; border: 2px solid {badge_color}; border-radius: 8px; padding: 16px; text-align: center;">
                        <span style="font-size: 11px; color: #666; font-weight: 600;">STATUS KESELARASAN</span>
                        <h2 style="color: {badge_color}; margin: 6px 0;">{status.upper()}</h2>
                        <span style="font-size: 12px; color: #888;">Tingkat Keyakinan: {int(eval_result['confidence']*100)}%</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with res_c2:
                st.markdown(f"**📌 Pertimbangan Hukum:** {eval_result['reasoning']}")
                st.markdown(f"**💡 Rekomendasi Aksi:** {eval_result['rekomendasi']}")
                
            st.markdown("#### 🔍 Komparasi Visual Redaksional (Diff):")
            diff_custom_html = render_side_by_side_diff_html(
                title_internal="Klausul Internal Pengujian",
                text_internal=custom_internal,
                title_regulasi="Regulasi Pemerintah Acuan",
                text_regulasi=custom_external,
                status=status,
                reasoning=eval_result["reasoning"],
            )
            st.markdown(diff_custom_html, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 3: Panduan Presentasi & Arsitektur
# ---------------------------------------------------------
with tab_about:
    st.markdown("### 💡 Panduan Presentasi untuk Rekan Kerja Bank Mandiri")
    st.markdown(
        """
        Gunakan poin-poin berikut saat mendemonstrasikan prototipe ini kepada atasan atau tim kepatuhan perbankan:
        
        1. **Pernyataan Masalah (Problem Statement)**:
           - *"Setiap kali OJK atau BI merilis POJK baru, tim legal/compliance menghabiskan waktu berminggu-minggu memvalidasi ratusan dokumen SOP secara manual."*
        2. **Solusi yang Ditawarkan (RegAlign / Big Legal Concept)**:
           - *"Prototipe ini membuktikan bahwa proses audit keselarasan dapat diotomatisasi secara terstruktur menjadi 3 status jelas: Selaras, Tidak Selaras, dan Netral."*
        3. **Nilai Tambah (Explainability & Visual Diff)**:
           - *"Sistem ini bukan sekadar kotak hitam (black-box). Ketika diklik, pimpinan bisa langsung melihat kalimat Before-After dengan kata yang bertentangan disorot warna merah, lengkap dengan alasan hukumnya."*
        4. **Keamanan & Roadmap Masa Depan (Privacy by Design)**:
           - *"Untuk tahap implementasi skala penuh, model AI ini dapat di-deploy secara On-Premise (server privat internal Bank Mandiri) sehingga dokumen rahasia bank tidak pernah keluar ke jaringan publik."*
        """
    )
