# Panduan Pitching dan Simulasi Demo 3 Menit: Mandiri RegAlign

Dokumen ini disusun sebagai panduan praktis bagi rekan kerja di Bank Mandiri saat mempresentasikan prototipe sistem **Mandiri RegAlign** kepada pimpinan unit kerja (Kepala Divisi Kepatuhan / Legal Officer / Tim Manajemen Risiko).

---

## 1. Ringkasan Strategi Presentasi

Pimpinan perbankan tidak membutuhkan penjelasan teknis kode yang berbelit-belit. Mereka berfokus pada 3 pertanyaan utama:
1. **Apa masalah nyata yang diselesaikan?** (Efisiensi audit manual vs risiko sanksi regulator).
2. **Bagaimana sistem ini membuktikannya secara nyata?** (Dashboard interaktif, visualisasi gap analysis, dan sorotan kata yang berbeda).
3. **Apakah data rahasia bank aman?** (Jaminan arsitektur on-premise private server).

---

## 2. Naskah Skenario Demo 3 Menit (Minute-by-Minute Script)

### Menit ke-1: Pembuka dan Pengangkatan Masalah (Problem Statement)
**Tindakan**: Buka peramban yang sudah menampilkan halaman utama aplikasi `http://localhost:8501`. Jangan langsung klik tombol apa pun, biarkan pimpinan melihat judul dokumen.

**Skrip Percakapan**:
> "Selamat pagi/siang Bapak/Ibu. Izin menyampaikan inisiatif percontohan yang sedang kami kembangkan untuk mempercepat proses uji kepatuhan regulasi di Bank Mandiri.
> 
> Seperti yang kita ketahui, setiap kali OJK, Bank Indonesia, atau kementerian menerbitkan regulasi baru, tim Legal dan Kepatuhan kita membutuhkan waktu berminggu-minggu untuk menelaah ribuan lembar dokumen Pedoman Operasional (PO) dan SOP internal.
> 
> Proses telaah manual ini bukan hanya memakan waktu dan tenaga, tetapi juga rentan terhadap kekeliruan manusia (human error). Keterlambatan penyesuaian klausul berisiko menimbulkan sanksi administratif dan denda kepatuhan dari regulator.
> 
> Melalui inisiatif Mandiri RegAlign ini, kami ingin membuktikan bahwa proses telaah kepatuhan tersebut dapat diotomatisasi secara terukur dan transparan."

---

### Menit ke-2: Demonstrasi Solusi Nyata (Live Demonstration)
**Tindakan**: Arahkan perhatian ke Donut Chart dan Kartu Metrik di bagian atas layar.

**Skrip Percakapan**:
> "Di layar utama ini, sistem langsung memberikan ringkasan status kepatuhan dari dokumen Petunjuk Operasional Ketahanan Siber dan Layanan Digital kita.
> 
> Dari 6 klausul uji yang dianalisis terhadap POJK 11/2022 dan UU Perlindungan Data Pribadi:
> - 2 klausul terkonfirmasi **Selaras** (memenuhi standar minimum regulator).
> - 2 klausul berstatus **Netral** (merupakan aturan teknis operasional internal).
> - 2 klausul terdeteksi **Tidak Selaras** dan berpotensi menimbulkan risiko hukum tinggi."

**Tindakan**: Gulir ke bawah ke daftar klausul. Klik klausul **PO-002 (Batas Waktu Pelaporan Insiden Kebocoran Data)**. Klik tombol **"Lihat Komparasi Before-After"**.

**Skrip Percakapan**:
> "Sistem ini bukan sekadar kotak hitam (black-box). Ketika kita klik tombol komparasi, muncul jendela perbandingan kalimat bersanding:
> 
> Di sebelah kiri adalah bunyi Petunjuk Operasional internal kita, dan di sebelah kanan adalah bunyi Pasal 46 UU PDP. Kata-kata yang bertentangan langsung disorot warna merah:
> - SOP internal kita masih mencantumkan batas waktu laporan selambat-lambatnya **7 hari kerja**.
> - Sedangkan ketentuan undang-undang mewajibkan laporan tertulis maksimal **3 x 24 jam**.
> 
> Di bagian bawah, sistem langsung menyertakan pertimbangan hukum ringkas dan rekomendasi perbaikan redaksional yang siap dieksekusi oleh tim legal."

**Tindakan**: Tutup dialog pop-up.

---

### Menit ke-3: Fleksibilitas Berkas Nyata, Laporan PDF, dan Keamanan Data (Closing)
**Tindakan**: Klik tab kedua: **"Unggah & Parsing Dokumen"**.

**Skrip Percakapan**:
> "Aplikasi ini juga fleksibel. Pada tab ini, kita dapat langsung mengunggah berkas dokumen asli dalam format Word (.docx) atau PDF regulasi. Sistem akan secara otomatis memecah isi dokumen menjadi hierarki Bab, Pasal, dan Ayat, lalu menjalankan komparasi semantik secara mandiri."

**Tindakan**: Arahkan kursor ke tombol di sidebar kiri: **"Unduh Laporan Formal (PDF)"**.

**Skrip Percakapan**:
> "Seluruh hasil audit ini dapat langsung diunduh dalam format PDF resmi Bank Mandiri, lengkap dengan matriks gap analysis untuk kebutuhan rapat komite maupun auditor eksternal."

**Tindakan**: Penutup mengenai isu keamanan data (Objection Handling).

**Skrip Percakapan**:
> "Sebagai penutup terkait keamanan data: Untuk tahap implementasi produksi penuh, arsitektur sistem ini dirancang untuk dijalankan secara on-premise di dalam pusat data privat Bank Mandiri. Dokumen rahasia bank tidak akan pernah dikirimkan ke jaringan internet publik.
> 
> Kami berharap inisiatif ini dapat disetujui untuk diuji coba lebih luas pada divisi operasional dan legal kita. Terima kasih."

---

## 3. Antisipasi Pertanyaan Pimpinan (Q&A / Objection Handling)

| Pertanyaan Pimpinan | Jawaban Taktis yang Direkomendasikan |
| :--- | :--- |
| **"Apakah model AI ini bisa menggantikan peran orang legal?"** | *"Sama sekali tidak menggantikan, Pak/Bu. Sistem ini bertindak sebagai asisten pemeriksa awal (first-line reviewer) untuk memilah ribuan pasal dalam hitungan detik. Keputusan akhir dan persetujuan kebijakan tetap 100% berada di tangan pejabat legal perbankan."* |
| **"Bagaimana jika dokumen SOP kita memiliki ratusan halaman?"** | *"Sistem telah dilengkapi modul parser dokumen hukum yang otomatis mengenali pola Bab, Bagian, dan Ayat. Pada fase pengembangan berikutnya, pencocokan antar pasal diperkuat dengan semantic vector search sehingga mampu menangani dokumen berukuran besar secara instan."* |
| **"Berapa lama waktu yang dibutuhkan untuk menerapkan ini secara resmi?"** | *"Prototipe MVP yang Bapak/Ibu lihat hari ini membuktikan bahwa algoritmanya sudah bekerja. Untuk integrasi ke server on-premise bank dan pengujian dataset penuh, estimasi waktu implementasi berkisar antara 4 hingga 8 minggu kerja."* |
