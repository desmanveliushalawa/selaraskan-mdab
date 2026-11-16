"""
rapat_teknis_manager.py
Modul pengelolaan data Riwayat Rapat Teknis dan Matriks Perubahan Kebijakan Internal Bank Mandiri.
Menyediakan audit trail kronologis per pasal/klausul yang diubah sebelum dan sesudah rapat teknis.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

RAPAT_TEKNIS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "rapat_teknis"
)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", slug)[:40]


def init_default_rapat_teknis():
    """Menginisialisasi data rapat teknis bawaan Bank Mandiri jika belum ada."""
    os.makedirs(RAPAT_TEKNIS_DIR, exist_ok=True)

    # 1. Rapat Teknis PTO KUR Bank Mandiri Edisi 8 (Januari 2026)
    default_rt_id = "rt_pto_kur_mandiri_edisi_8"
    file_path = os.path.join(RAPAT_TEKNIS_DIR, f"{default_rt_id}.json")

    if not os.path.exists(file_path):
        sample_data = {
            "id": default_rt_id,
            "target_doc_id": "Petunjuk Teknis Operasional Kredit Usaha Rakyat (KUR)",
            "meeting_date": "2026-01-13",
            "meeting_title": "Rapat Teknis Penyesuaian PTO KUR Edisi 8 (MDAB & SMR Group)",
            "organizer": "Micro Development & Agent Banking (MDAB) Group",
            "notes": "Penyesuaian ketentuan operasional KUR sesuai Permenko Perekonomian No. 1 Tahun 2026, penghapusan agunan tambahan limit s.d. 100 juta, dan penerapan skema bunga berjenjang.",
            "file_name": "Matriks_Perubahan_PTO_KUR_Edisi_8_Januari_2026.docx",
            "changes": [
                {
                    "clause_ref": "H. Agunan",
                    "sub_ref": "2. Agunan Tambahan",
                    "topic": "Penghapusan Ketentuan Agunan Tambahan KUR s.d. 100 Juta",
                    "before_text": "Unit Bisnis Mikro wajib meminta agunan tambahan berupa sertifikat tanah/bangunan atau BPKB untuk permohonan pinjaman KUR di atas Rp 50.000.000.",
                    "after_text": "KUR dengan limit kredit sampai dengan Rp 100.000.000,00 (seratus juta rupiah), dilarang mempersyaratkan dan/atau menerima Agunan Tambahan.",
                    "reason": "Penyesuaian wajib terhadap Permenko Perekonomian No. 1 Tahun 2026 Pasal 14 ayat (2).",
                },
                {
                    "clause_ref": "BAB III : KETENTUAN KUR - Suku Bunga",
                    "sub_ref": "Ketentuan Bunga",
                    "topic": "Penetapan Suku Bunga KUR Mikro Berjenjang",
                    "before_text": "Suku bunga pinjaman KUR Mikro dan KUR Kecil ditetapkan flat 6% efektif per tahun untuk seluruh siklus pinjaman debitur.",
                    "after_text": "Suku bunga pinjaman KUR Mikro ditetapkan 6% efektif per tahun untuk penyaluran pertama, dan berjenjang naik 7%, 8%, sampai 9% untuk debitur suplemen/berulang.",
                    "reason": "Implementasi skema graduasi suku bunga perbankan sesuai Permenko Perekonomian No. 1 Tahun 2026 Pasal 18 ayat (1) dan (2).",
                },
                {
                    "clause_ref": "G. Dokumen Persyaratan KUR",
                    "sub_ref": "Persyaratan Kepesertaan BPJS Ketenagakerjaan",
                    "topic": "Kewajiban Kepesertaan BPJS Ketenagakerjaan Limit > 100 Juta",
                    "before_text": "Calon debitur tidak dipersyaratkan memiliki kepesertaan jaminan sosial ketenagakerjaan.",
                    "after_text": "Untuk Debitur KUR Kecil dan KUR Khusus limit > Rp 100 juta dipersyaratkan bukti kepesertaan BPJS Ketenagakerjaan aktif.",
                    "reason": "Kepatuhan terhadap Instruksi Presiden No. 2 Tahun 2021 dan Permenko No. 1 Tahun 2026.",
                },
            ],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)

    # 2. Rapat Teknis PO IT Siber Mandiri (Simulasi Demo)
    demo_rt_id = "rt_po_dir_it_042_2024"
    demo_file_path = os.path.join(RAPAT_TEKNIS_DIR, f"{demo_rt_id}.json")
    if not os.path.exists(demo_file_path):
        sample_demo = {
            "id": demo_rt_id,
            "target_doc_id": "Petunjuk Operasional (PO) No. PO-DIR/IT/042/2024",
            "meeting_date": "2024-01-10",
            "meeting_title": "Rapat Teknis Penyelarasan Tata Kelola Siber & UU PDP Bank Mandiri",
            "organizer": "Group IT & Legal Compliance",
            "notes": "Penyelarasan ketentuan enkripsi AES-256 dan evaluasi tenggat waktu pelaporan insiden data pribadi.",
            "file_name": "Notulen_Rapat_Teknis_Ketahanan_Siber_Januari_2024.docx",
            "changes": [
                {
                    "clause_ref": "Pasal 4 Angka 2",
                    "sub_ref": "Enkripsi Data Sensitif",
                    "topic": "Enkripsi Data Sensitif Nasabah pada Penyimpanan dan Transmisi",
                    "before_text": "Bank Mandiri menerapkan enkripsi data nasabah sensitif dengan algoritma standar 3DES atau AES-128 saat transit.",
                    "after_text": "Bank Mandiri wajib menerapkan enkripsi data nasabah kategori sensitif (data finansial dan kredensial autentikasi) baik saat data disimpan (data-at-rest) dengan standar minimal AES-256 maupun saat data ditransmisikan (data-in-transit) menggunakan protokol kriptografi TLS 1.3.",
                    "reason": "Peningkatan standar keamanan enkripsi mengikuti ketentuan POJK No. 11/POJK.03/2022 dari AES-128 menjadi AES-256 dan TLS 1.3.",
                },
                {
                    "clause_ref": "Pasal 7 Angka 4",
                    "sub_ref": "Pelaporan Insiden",
                    "topic": "Batas Waktu Pelaporan Insiden Kebocoran Data Pribadi",
                    "before_text": "Dalam hal terjadi insiden kegagalan perlindungan data, Unit Kerja Pengelola Sistem wajib menyampaikan laporan investigasi kepada internal selambat-lambatnya 14 (empat belas) hari kerja.",
                    "after_text": "Dalam hal terjadi insiden kegagalan perlindungan atau dugaan kebocoran data nasabah, Unit Kerja Pengelola Sistem wajib menyampaikan laporan investigasi awal kepada Direksi dan regulator terkait selambat-lambatnya dalam jangka waktu 7 (tujuh) hari kerja setelah terkonfirmasi.",
                    "reason": "Penyelarasan awal masa transisi UU No. 27 Tahun 2022 (UU PDP), diperpendek dari 14 hari kerja menjadi 7 hari kerja (masih perlu penyelarasan akhir ke 3x24 jam kalender).",
                },
            ],
        }
        with open(demo_file_path, "w", encoding="utf-8") as f:
            json.dump(sample_demo, f, indent=2, ensure_ascii=False)


def list_rapat_teknis() -> List[Dict[str, Any]]:
    """Mengembalikan daftar seluruh riwayat rapat teknis yang tersimpan."""
    init_default_rapat_teknis()
    records = []
    for item in os.listdir(RAPAT_TEKNIS_DIR):
        if item.endswith(".json"):
            file_path = os.path.join(RAPAT_TEKNIS_DIR, item)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records.append({
                        "id": data.get("id", item.replace(".json", "")),
                        "target_doc_id": data.get("target_doc_id", ""),
                        "meeting_date": data.get("meeting_date", ""),
                        "meeting_title": data.get("meeting_title", ""),
                        "organizer": data.get("organizer", "Unit Kerja Bank Mandiri"),
                        "notes": data.get("notes", ""),
                        "total_changes": len(data.get("changes", [])),
                        "file_name": data.get("file_name", ""),
                    })
            except Exception:
                continue

    # Urutkan berdasarkan tanggal rapat terbaru
    records.sort(key=lambda r: r.get("meeting_date", ""), reverse=True)
    return records


def get_rapat_teknis(rt_id: str) -> Optional[Dict[str, Any]]:
    """Mengambil satu dokumen rapat teknis lengkap berdasarkan ID."""
    init_default_rapat_teknis()
    file_path = os.path.join(RAPAT_TEKNIS_DIR, f"{rt_id}.json")
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_rapat_teknis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Menyimpan atau memperbarui dokumen rapat teknis."""
    init_default_rapat_teknis()
    
    rt_id = data.get("id")
    if not rt_id:
        title_slug = _slugify(data.get("meeting_title", "rapat_teknis"))
        date_slug = _slugify(data.get("meeting_date", "2026-01-01"))
        rt_id = f"rt_{date_slug}_{title_slug}"

    data["id"] = rt_id
    file_path = os.path.join(RAPAT_TEKNIS_DIR, f"{rt_id}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data


def delete_rapat_teknis(rt_id: str) -> bool:
    """Menghapus dokumen rapat teknis berdasarkan ID."""
    init_default_rapat_teknis()
    file_path = os.path.join(RAPAT_TEKNIS_DIR, f"{rt_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def find_rapat_teknis_for_target(doc_title: str) -> List[Dict[str, Any]]:
    """
    Mencari seluruh dokumen rapat teknis yang berkaitan dengan judul dokumen target.
    Pencocokan dilakukan menggunakan kesamaan kata kunci substantif (token overlap).
    Hasil diurutkan berdasarkan skor relevansi tertinggi, lalu tanggal terlama ke terbaru.
    """
    init_default_rapat_teknis()
    matched_records = []
    
    stop_tokens = {
        "petunjuk", "operasional", "pedoman", "surat", "edaran", "standar", "prosedur",
        "bank", "mandiri", "nomor", "tahun", "tata", "kelola", "tentang", "dan", "yang"
    }

    target_clean = re.sub(r"[^\w\s]", " ", doc_title.lower())
    target_tokens = set(t for t in target_clean.split() if len(t) > 1 and t not in stop_tokens)

    for item in os.listdir(RAPAT_TEKNIS_DIR):
        if not item.endswith(".json"):
            continue
        file_path = os.path.join(RAPAT_TEKNIS_DIR, item)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        recorded_target = data.get("target_doc_id", "")
        rec_clean = re.sub(r"[^\w\s]", " ", recorded_target.lower())
        rec_tokens = set(t for t in rec_clean.split() if len(t) > 1 and t not in stop_tokens)

        # Cek irisan kata kunci substantif
        overlap = target_tokens.intersection(rec_tokens)
        if len(overlap) >= 1:
            score = len(overlap) / max(len(target_tokens), 1)
            matched_records.append((score, data))

    # Urutkan berdasarkan relevansi skor tertinggi terlebih dahulu
    matched_records.sort(key=lambda x: (x[0], x[1].get("meeting_date", "")), reverse=True)
    return [item[1] for item in matched_records]
