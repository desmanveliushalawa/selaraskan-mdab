# SELARASKAN MDAB : Sistem Uji Keselarasan Regulasi Perbankan

Sistem audit kepatuhan regulasi berbasis kecerdasan buatan (Regulatory Compliance and Alignment AI) yang dirancang untuk menguji keselarasan norma antara Petunjuk Operasional (SOP/PO) internal Bank Mandiri dengan regulasi pemerintah dan otoritas terkait (POJK, Bank Indonesia, UU Perlindungan Data Pribadi).

Konsep dan arsitektur sistem ini terinspirasi dari produk **Big Legal by BigBox (Telkom Indonesia)**, dibangun dengan standar desain institusional perbankan yang bebas dari ornamen generik kecerdasan buatan (Anti-Slop standard).

---

## 1. Latar Belakang Masalah

Bank Mandiri sebagai bank BUMN sistemik (KBMI 4) beroperasi di bawah pengawasan regulasi yang ketat. Setiap kali regulator menerbitkan Surat Edaran atau Peraturan Otoritas Jasa Keuangan (POJK) baru, tim Kepatuhan dan Hukum bank wajib menelaah ribuan lembar dokumen SOP internal.

Tantangan utama operasional saat ini:
1. **Audit Manual yang Memakan Waktu**: Memeriksa klausul internal secara manual membutuhkan waktu mingguan hingga bulanan.
2. **Risiko Sanksi Regulasi**: Keterlambatan atau kelalaian dalam menyesuaikan SOP berisiko menimbulkan sanksi administratif dan denda kepatuhan dari regulator.
3. **Ketiadaan Komparasi Visual Presisi**: Sulit mengidentifikasi deviasi kata per kata secara cepat antara kewajiban hukum eksternal dan petunjuk operasional internal.

SELARASKAN MDAB hadir untuk memvalidasi kelayakan otomasi proses uji keselarasan regulasi secara terukur, transparan, dan dapat dijelaskan (explainable AI).

---

## 2. Diagram Alir Sistem (Start to End)

Diagram alir berikut menggambarkan siklus penuh pemrosesan data pada SELARASKAN MDAB:

```mermaid
flowchart TD
    Start(["START: Pengguna Membuka Aplikasi"]) --> LoadDashboard["Inisialisasi Antarmuka Institusional Bank Mandiri"]
    
    LoadDashboard --> SelectAction{"Pilih Menu Operasi"}
    
    SelectAction -->|"Menu 1: Evaluasi Dokumen"| ViewBenchmark["Tampilkan Matriks Evaluasi & Donut Chart Kepatuhan"]
    SelectAction -->|"Menu 2: Unggah Berkas Baru"| UploadFile["Pengguna Mengunggah Berkas (.docx / .pdf / .txt)"]
    SelectAction -->|"Menu 3: Uji Mandiri"| CustomInput["Input Teks Klausul Internal & Teks Regulasi Acuan"]
    
    UploadFile --> ParseDoc["Legal Parser: Ekstraksi Struktur Hierarki (Bab, Pasal, Ayat)"]
    ParseDoc --> ShowMetadata["Tampilkan Statistik Ekstraksi: Total Bab, Pasal, Ayat"]
    
    ShowMetadata --> TriggerAutoAudit{"Jalankan Audit Otomatis?"}
    TriggerAutoAudit -->|"Ya"| SemanticRAG["Semantic Retrieval: TF-IDF Bi-gram & Cosine Similarity"]
    
    SemanticRAG --> MatchCandidate["Pasangkan Ayat dengan Pasal Regulasi Terdekat"]
    CustomInput --> EvaluateNLI["Evaluasi Keselarasan Semantik (NLI Engine)"]
    MatchCandidate --> EvaluateNLI
    
    EvaluateNLI --> TriStateClassification{"Klasifikasi 3 Status"}
    TriStateClassification -->|"Entailment"| StatusSelaras["Status: SELARAS (Hijau)"]
    TriStateClassification -->|"Contradiction"| StatusTidakSelaras["Status: TIDAK SELARAS (Merah)"]
    TriStateClassification -->|"Neutral"| StatusNetral["Status: NETRAL (Kuning)"]
    
    StatusSelaras --> GenDiff["Diff Engine: Komputasi Perbedaan Kata (difflib SequenceMatcher)"]
    StatusTidakSelaras --> GenDiff
    StatusNetral --> GenDiff
    
    GenDiff --> RenderCard["Render Kartu Hasil: Status, Reasoning, & Rekomendasi"]
    
    ViewBenchmark --> UserClickDiff{"Klik 'Lihat Komparasi Before-After'"}
    RenderCard --> UserClickDiff
    
    UserClickDiff -->|"Ya"| OpenDialog["Buka Modal Pop-up: Teks Bersanding dengan Sorotan Merah"]
    
    SelectAction -->|"Unduh Laporan"| ExportChoice{"Pilih Format Laporan"}
    ExportChoice -->|"Laporan PDF Formal"| GeneratePDF["ReportLab Engine: Cetak Laporan PDF Resmi Bank Mandiri"]
    ExportChoice -->|"Rekapitulasi CSV"| GenerateCSV["Ekspor Dataframe ke Berkas CSV"]
    
    GeneratePDF --> End(["END: Laporan Siap Digunakan untuk Rapat Komite"])
    GenerateCSV --> End
```

---

## 3. Daftar Tools dan Teknologi yang Digunakan

| Komponen | Pustaka / Teknologi | Versi | Peran dalam Sistem |
| :--- | :--- | :--- | :--- |
| **Bahasa Pemrograman** | Python | 3.10 - 3.12 | Bahasa utama implementasi pipeline dan logika sistem |
| **Kerangka Kerja Antarmuka** | Streamlit | 1.37+ | Antarmuka interaktif, tata letak dua kolom, dan modal dialog (`@st.dialog`) |
| **Visualisasi Data** | Plotly Graph Objects | 6.0+ | Diagram donat interaktif distribusi tingkat kepatuhan regulasi |
| **Legal Document Parser** | Python-docx & PyPDF | docx 1.2+, pypdf 6.2+ | Ekstraksi teks dan penguraian struktur Bab/Pasal/Ayat dari Word dan PDF |
| **Semantic Retrieval (RAG)** | Scikit-Learn | 1.5+ | Pencocokan otomatis pasal acuan berbasis TF-IDF bi-gram dan Cosine Similarity |
| **Diff Highlighter Engine** | Python `difflib` | Modul Standar | Komparasi redaksional kata per kata (`SequenceMatcher`) dan penandaan warna |
| **Generator Laporan Resmi** | ReportLab | 5.1+ | Pembuatan berkas laporan audit resmi PDF berstandar perbankan nasional |
| **Manipulasi Data** | Pandas | 2.0+ | Manajemen tabel data, pemfilteran klausul, dan ekspor CSV |

---

## 4. Panduan Menjalankan Prototipe di Komputer Lokal

### Prasyarat
Pastikan komputer Anda telah terpasang **Python** (versi 3.10, 3.11, atau 3.12) dan **Git**.

### Langkah 1: Kloning Repositori
```bash
git clone https://github.com/desmanveliushalawa/selaraskan-mdab.git
cd selaraskan-mdab
```

### Langkah 2: Buat dan Aktifkan Lingkungan Virtual (Rekomendasi)
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS (Bash)
python3 -m venv .venv
source .venv/bin/activate
```

### Langkah 3: Pasang Dependensi
```bash
pip install -r requirements.txt
```

### Langkah 4: Jalankan Unit Test (Verifikasi Sistem)
```bash
python -m unittest discover -s tests -v
```
Seluruh 15 unit test wajib berstatus `OK` (100% Pass).

### Langkah 5: Jalankan Aplikasi Streamlit
```bash
streamlit run app.py
```
Aplikasi otomatis terbuka di peramban web pada alamat `http://localhost:8501`.

---

## 5. Panduan Penggunaan Fitur Sistem

### Tab 1: Matriks Keselarasan Dokumen
1. Menampilkan ringkasan metrik kepatuhan dokumen Petunjuk Operasional TI Bank Mandiri terhadap POJK 11/2022 dan UU PDP.
2. Di sebelah kiri terdapat penelusuran hierarki dokumen (Bab II sampai Bab V).
3. Di sebelah kanan terdapat kartu hasil evaluasi dengan tiga badge status:
   - **SELARAS**: SOP memenuhi atau melampaui standar kementerian/regulator.
   - **TIDAK SELARAS**: Ditemukan pertentangan atau deviasi batas kepatuhan.
   - **NETRAL**: Ketentuan teknis prosedural internal bank yang tidak bertentangan.
4. Klik tombol **"Lihat Komparasi Before-After"** untuk membuka jendela pop-up perbandingan kalimat bersanding dengan kata-kata yang bertentangan disorot warna merah.
5. Unduh laporan formal melalui tombol **"Unduh Laporan Formal (PDF)"** di sidebar kiri.

### Tab 2: Unggah dan Parsing Dokumen (Legal Parser)
1. Unggah berkas dokumen SOP atau regulasi baru berformat `.docx`, `.pdf`, atau `.txt`.
2. Sistem otomatis membaca teks dan menghitung total Bab, total Pasal, dan total Ayat.
3. Klik tombol **"Jalankan Uji Keselarasan untuk Dokumen Ini"** untuk menjalankan pencarian semantik (Semantic Retrieval) yang otomatis memetakan setiap ayat ke korpus regulasi pemerintah terkait.

### Tab 3: Uji Klausul Mandiri
1. Masukkan teks draf klausul internal bank pada kolom kiri.
2. Masukkan teks pasal regulasi rujukan pada kolom kanan.
3. Klik tombol **"Jalankan Uji Keselarasan"** untuk melihat inferensi status kepatuhan, pertimbangan hukum ringkas, dan visualisasi diff kata per kata.

### Tab 4: Arsitektur dan Panduan
1. Memuat penjelasan metodologi Natural Language Inference (NLI) dan mitigasi risiko kerahasiaan data perbankan melalui skema implementasi privat on-premise.

---

## 6. Struktur Berkas Repositori

```
selaraskan-mdab/
├── app.py                      # Antarmuka utama aplikasi Streamlit
├── data/
│   └── bank_mandiri_demo.json  # Korpus studi kasus Petunjuk Operasional Bank Mandiri
├── engine/
│   ├── __init__.py             # Inisialisasi package engine
│   ├── alignment_engine.py     # Logika inferensi NLI dan perhitungan metrik kepatuhan
│   ├── diff_highlighter.py     # Generator perbandingan kata bersanding (word-level diff)
│   ├── legal_parser.py         # Ekstraktor hierarki Bab/Pasal/Ayat dari DOCX dan PDF
│   ├── report_generator.py     # Generator dokumen laporan audit formal PDF (ReportLab)
│   └── semantic_retriever.py   # Mesin pencari semantik pasal acuan berbasis TF-IDF & Cosine
├── tests/
│   ├── test_engine.py          # Pengujian unit diff highlighter & alignment engine
│   ├── test_parser.py          # Pengujian unit ekstraktor dokumen hukum
│   ├── test_report_generator.py# Pengujian unit generator laporan PDF
│   └── test_retriever.py       # Pengujian unit mesin pencari semantik
├── panduan_pitching_demo.md    # Naskah simulasi presentasi 3 menit di depan pimpinan
├── road_map.md                 # Peta jalan pengembangan Fase 1 s.d. Fase 4
├── requirements.txt            # Daftar pustaka dependensi Python
└── README.md                   # Dokumentasi resmi proyek
```

---

## 7. Keamanan Data dan Implementasi On-Premise

Untuk kebutuhan implementasi produksi di lingkungan Bank Mandiri:
- Arsitektur ini dirancang untuk dapat di-deploy secara **On-Premise** menggunakan infrastruktur server privat Bank Mandiri (menggunakan vLLM atau Ollama dengan model open-source seperti Llama-3-70B atau IndoLLM).
- Tidak ada data rahasia perbankan atau klausul internal yang dikirimkan ke penyedia komputasi awan pihak ketiga tanpa enkripsi dan persetujuan otoritas terkait.
