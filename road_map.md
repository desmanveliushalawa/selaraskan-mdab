# Roadmap Pengembangan & Kebutuhan Prasyarat Proyek Uji Keselarasan Regulasi (Mandiri RegAlign)

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
| `requests` | Komunikasi HTTP dengan API LLM eksternal / endpoint on-premise. | **Sudah Terpasang (v2.34.2)** |

---

### C. Persiapan Akun & Kredensial AI (Opsional / Dual-Engine)
Untuk menjaga agar aplikasi dapat didemokan tanpa risiko kegagalan koneksi:
1. **Mode 1: Offline / Pre-computed Engine (Wajib untuk Demo Awal)**:
   - Tidak memerlukan API Key atau biaya apapun.
   - Menggunakan dataset terkurasi Bank Mandiri vs POJK/BI/UU PDP yang disimpan secara lokal.
   - Menghasilkan respon instan (0 detik latensi), sangat andal di depan pimpinan.
2. **Mode 2: Live LLM Reasoning Engine (Untuk Uji Fleksibilitas Dokumen Baru)**:
   - Dapat menggunakan **Google Gemini API** (`GEMINI_API_KEY`) atau **OpenAI API** (`OPENAI_API_KEY`) via file `.env`.
   - Untuk lingkungan bank di masa depan (*production*): **Local LLM On-Premise** (Ollama / vLLM dengan Llama-3-70B / IndoLLM di private server Mandiri).

---

### D. Dataset & Dokumen Regulasi Uji Coba
Bahan dokumen yang disiapkan untuk studi kasus:
- **Internal Bank Mandiri**: Petunjuk Operasional (PO) No. PO-DIR/IT/042/2024 tentang Ketahanan Siber & Operasional Perbankan Digital.
- **Regulasi Regulator Rujukan**:
  1. *POJK No. 11/POJK.03/2022* (Penyelenggaraan Teknologi Informasi oleh Bank Umum).
  2. *UU No. 27 Tahun 2022* (Pelindungan Data Pribadi / UU PDP).
  3. *PADG Bank Indonesia No. 24/7/PADG/2022* (Penyelenggaraan Sistem Pembayaran).

---

## 2. Roadmap Pengembangan Sistem (Fase 1 s.d. Fase 4)

Berikut tahapan sistematis dari pembuktian konsep (PoC MVP) hingga kesiapan skala enterprise (*Production Ready*):

### 🟢 FASE 1: MVP Prototipe & Interactive Demo (Target Saat Ini)
**Tujuan**: Membuktikan konsep kepada rekan dan pimpinan Bank Mandiri bahwa proyek ini dapat dijelaskan dengan gamblang, memiliki UI interaktif Before-After diff, serta menampilkan status *Selaras, Tidak Selaras, Netral*.

- [x] **Milestone 1.1**: Analisis mendalam, audit keselarasan, dan diagram alir arsitektur.
- [x] **Milestone 1.2**: Pembuatan dataset benchmark realistis perbankan (`bank_mandiri_demo.json`).
- [ ] **Milestone 1.3**: Pembangunan modul `diff_highlighter.py` (word-level sequence diff dengan penandaan warna merah/hijau).
- [ ] **Milestone 1.4**: Pembangunan UI Streamlit (`app.py`):
  - Dashboard eksekutif: kartu metrik & donut chart Plotly (Positif, Negatif, Netral).
  - Tata letak 2 kolom ala Big Legal: Panel Kiri (Navigasi Bab/Pasal) & Panel Kanan (Kartu Regulasi Pasangan).
  - Modal pop-up dialog (`st.dialog`) untuk fitur interaktif *Before-After*.
- [ ] **Milestone 1.5**: Fitur *Custom Clause Tester* (input bebas klausul internal vs kementerian).
- [ ] **Milestone 1.6**: Pengujian end-to-end & penyusunan panduan simulasi presentasi demo.

---

### 🟡 FASE 2: Legal Document Parser & Hierarchical Chunking
**Tujuan**: Mengotomatisasi pembacaan dokumen panjang utuh (.docx dan .pdf) tanpa perlu entri manual.

- [ ] **Milestone 2.1**: Pembangunan parser khusus format dokumen hukum Indonesia:
  - Ekstraksi bagian Pembuka (Menimbang, Mengingat, Menetapkan).
  - Pemisahan Bab, Bagian, Paragraf, Pasal, Ayat, dan Huruf/Angka.
- [ ] **Milestone 2.2**: Metadata tagging otomatis (nomor regulasi, tahun penerbitan, otoritas penerbit: OJK/BI/Kemenkeu).
- [ ] **Milestone 2.3**: Penanganan dokumen yang dipindai (OCR menggunakan Tesseract / Surah OCR jika PDF berupa scan gambar).

---

### 🟠 FASE 3: Semantic Retrieval & Scale-Up Matching (RAG Engine)
**Tujuan**: Mengatasi pencocokan otomatis ketika dokumen internal memiliki ratusan pasal dan diuji terhadap puluhan regulasi eksternal ($N \times M$ matching).

- [ ] **Milestone 3.1**: Inisialisasi Vector Database lokal yang ringan (ChromaDB / FAISS / DuckDB-vss).
- [ ] **Milestone 3.2**: Implementasi Hybrid Search:
  - BM25 (pencarian kata kunci hukum yang kaku/spesifik).
  - Dense Semantic Embeddings (BGE-M3 atau OpenAI Embedding untuk kesamaan makna).
- [ ] **Milestone 3.3**: Cross-Encoder Reranker untuk memilih Top-3 kandidat pasal kementerian yang paling tepat untuk setiap klausul bank.
- [ ] **Milestone 3.4**: Prompt Engineering khusus penalaran hukum perbankan (*Chain-of-Thought Legal Reasoning*).

---

### 🔵 FASE 4: Enterprise Production & Keamanan Perbankan Mandiri
**Tujuan**: Penyesuaian standar operasional perbankan tingkat bank nasional (keamanan data, audit, dan integrasi sistem).

- [ ] **Milestone 4.1**: Penerapan **On-Premise Private LLM** (Ollama / vLLM dengan model Llama-3-70B di server lokal Bank Mandiri) sehingga data dokumen internal tidak pernah keluar dari jaringan bank.
- [ ] **Milestone 4.2**: Ekspor Laporan Resmi:
  - Fitur cetak laporan audit keselarasan berformat PDF resmi dan Excel (*Gap Analysis Sheet*) untuk diserahkan ke auditor kepatuhan internal/eksternal.
- [ ] **Milestone 4.3**: Role-Based Access Control (RBAC):
  - Pemisahan hak akses antara *Reviewer/Legal Officer* (bisa mengubah status/revisi) dan *Auditor/Viewer* (hanya baca).
- [ ] **Milestone 4.4**: Audit Log Trail untuk merekam riwayat verifikasi klausul.

---

## 3. Checklist Tindakan Segera (Immediate Action Plan)

Untuk menyelesaikan **Fase 1 (MVP)** hari ini:
1. Buat modul engine `engine/diff_highlighter.py` untuk menghasilkan perbandingan kata.
2. Buat engine penalaran `engine/alignment_engine.py` untuk evaluasi 3 status (*Selaras, Tidak Selaras, Netral*).
3. Bangun aplikasi utama `app.py` menggunakan Streamlit dan Plotly.
4. Lakukan pengujian eksekusi lokal dan verifikasi tampilan Before-After.

