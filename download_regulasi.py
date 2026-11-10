"""
download_regulasi.py
Skrip otomatis untuk mengunduh naskah asli regulasi perbankan Indonesia
ke dalam direktori 'regulasi_acuan/':
1. UU No. 27 Tahun 2022 (Pelindungan Data Pribadi) dari BPK RI
2. POJK No. 11/POJK.03/2022 (Penyelenggaraan TI oleh Bank Umum) dari OJK
3. Ringkasan POJK No. 11/POJK.03/2022 dari OJK
4. PADG BI No. 24/7/PADG/2022 (Penyelenggaraan Sistem Pembayaran) dari Bank Indonesia
"""

import os
import subprocess
import urllib.request

DEST_DIR = os.path.join(os.path.dirname(__file__), "regulasi_acuan")
os.makedirs(DEST_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

REGULATIONS = [
    {
        "filename": "UU_No_27_Tahun_2022_Pelindungan_Data_Pribadi.pdf",
        "url": "https://peraturan.bpk.go.id/Download/229798/UU%20Nomor%2027%20Tahun%202022.pdf",
    },
    {
        "filename": "POJK_No_11_POJK03_2022_Penyelenggaraan_TI_Bank_Umum.pdf",
        "url": "https://ojk.go.id/id/regulasi/Documents/Pages/Penyelenggaraan-Teknologi-Informasi-Oleh-Bank-Umum/POJK%2011%20-%2003%20-%202022.pdf",
    },
    {
        "filename": "RINGKASAN_POJK_11_03_2022.pdf",
        "url": "https://ojk.go.id/id/regulasi/Documents/Pages/Penyelenggaraan-Teknologi-Informasi-Oleh-Bank-Umum/RINGKASAN%20POJK%2011%20-%2003%20-%202022.pdf",
    },
    {
        "filename": "PADG_BI_No_24_7_PADG_2022_Sistem_Pembayaran.pdf",
        "url": "https://www.bi.go.id/id/publikasi/peraturan/Documents/PADG_240722.pdf",
    },
]


def download_all():
    print(f"Mengunduh dokumen regulasi ke: {DEST_DIR}")
    for item in REGULATIONS:
        dest_path = os.path.join(DEST_DIR, item["filename"])
        print(f"Mengunduh {item['filename']}...")
        cmd = [
            "curl.exe",
            "-L",
            "-s",
            "-o",
            dest_path,
            item["url"],
            "-H",
            f"User-Agent: {HEADERS['User-Agent']}",
        ]
        res = subprocess.run(cmd)
        if res.returncode == 0 and os.path.exists(dest_path):
            size_kb = round(os.path.getsize(dest_path) / 1024, 1)
            print(f"Berhasil: {item['filename']} ({size_kb} KB)")
        else:
            print(f"Gagal mengunduh: {item['filename']}")


if __name__ == "__main__":
    download_all()
