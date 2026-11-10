# Mandiri RegAlign: Uji Keselarasan Regulasi Perbankan

Prototipe AI Kepatuhan Hukum & Uji Keselarasan Regulasi (*Regulatory Compliance & Alignment AI*) yang membandingkan Petunjuk Operasional (PO/SOP) internal Bank Mandiri dengan regulasi regulator (POJK, Bank Indonesia, UU PDP). 

Terinspirasi dari konsep dan antarmuka produk **Big Legal by BigBox (Telkom Indonesia)**.

---

## 🌟 Fitur Utama

1. **Dashboard Eksekutif (KPI & Donut Chart)**:
   - Visualisasi persentase tingkat keselarasan dokumen (*Selaras, Tidak Selaras, Netral*).
   - Menghitung risiko kepatuhan secara otomatis.
2. **Navigasi Hirarki Dokumen (Panel Kiri & Kanan)**:
   - Penelusuran terstruktur: Judul $\rightarrow$ Bab $\rightarrow$ Pasal $\rightarrow$ Ayat.
   - Kartu perbandingan klausul internal bank vs regulasi pemerintah.
3. **Interactive Before-After Diff (Modal Pop-up)**:
   - Dialog bersanding (*side-by-side*) yang menyorot perbedaan kata kunci dengan warna merah/hijau menggunakan modul `difflib.SequenceMatcher`.
4. **Pertimbangan Hukum & Rekomendasi (Explainable AI)**:
   - Setiap evaluasi dilengkapi alasan hukum ringkas dan rekomendasi revisi kebijakan.
5. **Uji Klausul Kustom (Live Testing)**:
   - Pengguna dapat mengetik atau menempelkan klausul baru untuk dievaluasi secara dinamis.
6. **Ekspor Laporan Audit**:
   - Unduh hasil audit kepatuhan dalam format CSV.

---

## 🚀 Cara Menjalankan Aplikasi

Pastikan Python telah terpasang di komputer Anda (rekomendasi Python 3.10 - 3.12).

1. Buka terminal pada folder proyek:
   ```bash
   cd "d:\Project Desman\selaras"
   ```

2. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run app.py
   ```

3. Buka peramban pada alamat lokal yang muncul (biasanya `http://localhost:8501`).

---

## 📁 Struktur Berkas

```
selaras/
├── app.py                      # Aplikasi antarmuka Streamlit utama
├── data/
│   └── bank_mandiri_demo.json  # Data studi kasus realistis Bank Mandiri vs POJK/BI/UU PDP
├── engine/
│   ├── __init__.py
│   ├── diff_highlighter.py     # Generator HTML komparasi kata Before-After (diff)
│   └── alignment_engine.py     # Engine evaluasi keselarasan & pertimbangan hukum
├── tests/
│   └── test_engine.py          # Unit tests modul engine
├── road_map.md                 # Rencana pengembangan Fase 1 s.d. Fase 4
├── requirements.txt            # Dependensi pustaka Python
└── README.md                   # Dokumentasi proyek
```

---

## 🧪 Menjalankan Pengujian Otomatis

Untuk memastikan semua modul berjalan normal:
```bash
python -m unittest discover -s tests
```

