# Roadmap Pengembangan & Kebutuhan Prasyarat Proyek Uji Keselarasan Regulasi (SELARASKAN MDAB)

Dokumen ini memuat **daftar tools, teknologi, dan kebutuhan persiapan (*prerequisites*)**, serta **roadmap bertahap (Fase 1 s.d. Fase 4)** untuk membangun prototipe AI Uji Keselarasan Regulasi (*Regulatory Compliance & Alignment*) berstandar perbankan.

---

## 1. Daftar Tools, Library & Kebutuhan yang Harus Disiapkan

### A. Lingkungan Pengembangan (Development Environment)
| Komponen | Spesifikasi / Tool | Keterangan & Status |
| :--- | :--- | :--- |
| **Bahasa Pemrograman** | Python 3.10 – 3.12 | Versi terpasang di sistem: **Python 3.12.5** (Siap). |
| **Version Control** | Git | Untuk pelacakan perubahan kode dan kolaborasi tim. |
| **Terminal / CLI** | PowerShell / Bash | Untuk eksekusi server lokal dan pengujian. |
| **Code Editor** | VS Code / Cursor / IDE | Untuk pengeditan kode dan visualisasi. |

---

### B. Library & Framework Python
| Library | Fungsi Utama | Status di Environment |
| :--- | :--- | :--- |
| `streamlit` (v1.37+) | Framework antarmuka web interaktif utama, mendukung `@st.dialog` (modal pop-up). | **Sudah Terpasang (v1.37.1)** |
| `plotly` (v6.0+) | Visualisasi Donut Chart dan Bar Chart distribusi kepatuhan (*Selaras, Tidak Selaras, Netral*). | **Sudah Terpasang (v6.2.0)** |
| `difflib` | Modul standar bawaan Python untuk komparasi kata (*SequenceMatcher*) dan penandaan warna diff (Before-After). | **Bawaan Python (Siap)** |
| `re` (RegEx) | Ekstraksi pola hirarki dokumen hukum Indonesia (`BAB [IVXLCDM]+`, `Pasal \d+`, `Ayat \(\d+\)`). | **Bawaan Python (Siap)** |
| `python-docx` | Ekstraksi teks dari berkas regulasi berformat Word (.docx). | **Sudah Terpasang (v1.2.0)** |
| `pypdf` | Pembacaan dan ekstraksi berkas regulasi resmi pemerintah berformat PDF (.pdf). | **Sudah Terpasang (v6.20.1)** |
| `reportlab` | Pembuatan laporan resmi kepatuhan berformat PDF formal perbankan. | **Sudah Terpasang (v5.1.0)** |
| `scikit-learn` | Semantic retrieval berbasis TF-IDF bi-gram & cosine similarity. | **Sudah Terpasang (v1.5.2)** |

---

## 2. Roadmap Pengembangan Sistem (Fase 1 s.d. Fase 4)

### FASE 1: MVP Prototipe & Interactive Demo (SELESAI)
**Tujuan**: Membuktikan konsep kepada rekan dan pimpinan Bank Mandiri bahwa proyek ini dapat dijelaskan dengan gamblang, memiliki UI interaktif Before-After diff, serta menampilkan status *Selaras, Tidak Selaras, Netral*.

- [x] **Milestone 1.1**: Analisis mendalam, audit keselarasan, dan diagram alir arsitektur.
- [x] **Milestone 1.2**: Pembuatan dataset benchmark realistis perbankan (`bank_mandiri_demo.json`).
- [x] **Milestone 1.3**: Pembangunan modul `diff_highlighter.py` (word-level sequence diff dengan penandaan warna merah/hijau).
- [x] **Milestone 1.4**: Pembangunan UI Streamlit (`app.py`) Anti-Slop (desain institusional perbankan, 0% emoji, tanpa gradien generik).
- [x] **Milestone 1.5**: Fitur *Custom Clause Tester* (input bebas klausul internal vs kementerian).
- [x] **Milestone 1.6**: Pengujian end-to-end (15 unit test berhasil 100%).

---

### FASE 2: Legal Document Parser & Hierarchical Chunking (SELESAI)
**Tujuan**: Mengotomatisasi pembacaan dokumen panjang utuh (.docx dan .pdf) tanpa perlu entri manual.

- [x] **Milestone 2.1**: Pembangunan parser khusus format dokumen hukum Indonesia (`engine/legal_parser.py`):
  - Ekstraksi bagian Pembuka dan estimasi judul.
  - Pemisahan Bab, Pasal, Ayat, dan Butir secara otomatis.
- [x] **Milestone 2.2**: Metadata tagging otomatis (total Bab, total Pasal, total Ayat, ukuran berkas).
- [x] **Milestone 2.3**: Integrasi tab *Unggah & Parsing Dokumen* pada antarmuka Streamlit.

---

### FASE 3: Semantic Retrieval & Scale-Up Matching (RAG Engine) (SELESAI)
**Tujuan**: Mengatasi pencocokan otomatis ketika dokumen internal memiliki ratusan pasal dan diuji terhadap puluhan regulasi eksternal ($N \times M$ matching).

- [x] **Milestone 3.1**: Inisialisasi korpus regulasi perbankan nasional (POJK 11/2022, UU PDP, PADG BI).
- [x] **Milestone 3.2**: Implementasi *SemanticRetriever* (`engine/semantic_retriever.py`) dengan TF-IDF bi-gram, stopword hukum Indonesia, dan Cosine Similarity.
- [x] **Milestone 3.3**: Pemetaan otomatis klausul hasil unggahan terhadap regulasi acuan terdekat beserta skor relevansi semantik.
- [x] **Milestone 3.4**: Pembuatan modul Laporan Audit Formal PDF (`engine/report_generator.py`) dan tombol unduh langsung di aplikasi.
- [x] **Milestone 3.5**: Penyusunan panduan naskah pitching demo 3 menit (`panduan_pitching_demo.md`).

---

### FASE 4: Enterprise Production & Keamanan Perbankan Mandiri (Next Step)
**Tujuan**: Penyesuaian standar operasional perbankan tingkat bank nasional (keamanan data, audit, dan integrasi sistem).

- [ ] **Milestone 4.1**: Penerapan **On-Premise Private LLM** (Ollama / vLLM dengan model Llama-3-70B di server lokal Bank Mandiri).
- [ ] **Milestone 4.2**: Role-Based Access Control (RBAC): pemisahan hak akses antara Reviewer/Legal Officer dan Auditor/Viewer.
- [ ] **Milestone 4.3**: Audit Log Trail untuk merekam riwayat verifikasi klausul dan approval pengesahan revisi.
