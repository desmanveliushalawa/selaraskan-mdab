"""
bucket_manager.py
Modul manajemen Bucket Dokumen Acuan (Knowledge Base Management).
Memungkinkan pengguna membuat koleksi dokumen acuan secara fleksibel:
- Bucket Regulasi Eksternal (Pemerintah & OJK)
- Bucket Kebijakan Internal (Tier-1 Policy Bank Mandiri)
- Bucket Petunjuk Operasional / Juknis (Tier-2 SOP)
- Bucket Kustom yang dibuat dan diunggah mandiri oleh pengguna.
"""

import json
import os
import re
import shutil
from typing import Any, Dict, List, Optional
from engine.legal_parser import extract_raw_text, parse_legal_structure
from engine.semantic_retriever import SemanticRetriever, DEFAULT_REGULATORY_CORPUS

BUCKETS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "buckets")

# Cache memori untuk retriever per bucket agar query semantik instan
_RETRIEVER_CACHE: Dict[str, SemanticRetriever] = {}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", slug)[:40]


def init_default_buckets():
    """Menginisialisasi bucket bawaan perbankan jika belum ada."""
    os.makedirs(BUCKETS_BASE_DIR, exist_ok=True)

    # 1. Bucket Regulasi Eksternal (Pemerintah & OJK)
    b1_id = "bucket_regulasi_eksternal_ojk"
    b1_dir = os.path.join(BUCKETS_BASE_DIR, b1_id)
    if not os.path.exists(b1_dir):
        os.makedirs(os.path.join(b1_dir, "documents"), exist_ok=True)
        meta_1 = {
            "id": b1_id,
            "name": "Regulasi Pemerintah, OJK, dan Bank Indonesia",
            "category": "Regulasi Eksternal (Regulator)",
            "description": "Ketentuan Acuan Nasional: POJK No. 11/2022 (TI Bank), UU No. 27/2022 (UU PDP), PADG BI No. 24/7/2022, dan Permenko Perekonomian No. 1/2023 (Pedoman KUR).",
            "is_default": True,
            "files": [
                "POJK_No_11_POJK03_2022_Penyelenggaraan_TI_Bank_Umum.pdf",
                "UU_No_27_Tahun_2022_Pelindungan_Data_Pribadi.pdf",
                "PADG_BI_No_24_7_PADG_2022_Sistem_Pembayaran.pdf",
                "Permenko_Perekonomian_No_1_Tahun_2023_Pedoman_KUR.pdf",
            ],
            "clauses": DEFAULT_REGULATORY_CORPUS,
        }
        with open(os.path.join(b1_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta_1, f, indent=2, ensure_ascii=False)

    # 2. Bucket Kebijakan Internal Perkreditan Bank Mandiri (Tier-1 Policy)
    b2_id = "bucket_kebijakan_kredit_mandiri"
    b2_dir = os.path.join(BUCKETS_BASE_DIR, b2_id)
    if not os.path.exists(b2_dir):
        os.makedirs(os.path.join(b2_dir, "documents"), exist_ok=True)
        # Ekstrak atau muat klausul KPKD Mandiri
        sample_kpkd_clauses = [
            {
                "id": "KPKD-01",
                "regulasi_terkait": "Kebijakan Perkreditan Bank Mandiri",
                "pasal_regulasi": "Artikel 200",
                "topik": "Penerapan Prinsip Kehati-hatian dan Manajemen Risiko Kredit",
                "teks_regulasi": "Seluruh unit bisnis perkreditan Bank Mandiri wajib menerapkan prinsip kehati-hatian (prudential banking) dalam setiap proses analisis, persetujuan, dan pencairan fasilitas kredit guna menjaga kualitas aset produktif bank.",
            },
            {
                "id": "KPKD-02",
                "regulasi_terkait": "Kebijakan Perkreditan Bank Mandiri",
                "pasal_regulasi": "Artikel 540",
                "topik": "Persyaratan Jaminan dan Agunan Fasilitas Kredit",
                "teks_regulasi": "Setiap penyaluran fasilitas kredit komersial dan konsumer wajib didukung agunan pokok yang memadai. Untuk program kredit tertentu yang dijamin oleh pemerintah, persyaratan agunan tambahan wajib mematuhi ketentuan perundang-undangan program terkait.",
            },
            {
                "id": "KPKD-03",
                "regulasi_terkait": "Kebijakan Perkreditan Bank Mandiri",
                "pasal_regulasi": "Artikel 500",
                "topik": "Proses Persetujuan Kredit dan Penerapan Four-Eye Principle",
                "teks_regulasi": "Pemberian persetujuan kredit harus dilakukan secara independen dengan menerapkan four-eye principle yang melibatkan Unit Bisnis dan Unit Manajemen Risiko Kredit sesuai batas wewenang memutus kredit.",
            },
            {
                "id": "KPKD-04",
                "regulasi_terkait": "Kebijakan Perkreditan Bank Mandiri",
                "pasal_regulasi": "Artikel 630",
                "topik": "Kepatuhan Produk Kredit Program Khusus UMKM dan KUR",
                "teks_regulasi": "Penyaluran kredit program bersubsidi pemerintah seperti Kredit Usaha Rakyat (KUR) wajib tunduk pada pedoman teknis yang diterbitkan oleh kementerian koordinator dan komite kebijakan KUR nasional.",
            },
            {
                "id": "KPKD-05",
                "regulasi_terkait": "Kebijakan Perkreditan Bank Mandiri",
                "pasal_regulasi": "Artikel 300",
                "topik": "Manajemen Risiko Portofolio dan Batas Konsentrasi Pembiayaan",
                "teks_regulasi": "Bank menetapkan batas toleransi risiko (risk appetite) dan konsentrasi portofolio pembiayaan per sektor industri guna memitigasi potensi pemburukan Non-Performing Loan (NPL).",
            },
        ]
        meta_2 = {
            "id": b2_id,
            "name": "Kebijakan Perkreditan Internal Bank Mandiri (Tier-1 Policy)",
            "category": "Kebijakan Induk Internal",
            "description": "Kebijakan Perkreditan (KPKD) PT Bank Mandiri (Persero) Tbk: Landasan filosofi kredit, Prinsip Kehati-hatian (Artikel 200), Agunan (Artikel 540), Persetujuan Kredit (Artikel 500), dan Produk Khusus.",
            "is_default": True,
            "files": ["Kebijakan_Perkreditan_Bank_Mandiri_i3655.pdf"],
            "clauses": sample_kpkd_clauses,
        }
        with open(os.path.join(b2_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta_2, f, indent=2, ensure_ascii=False)

    # 3. Bucket Juknis Operasional KUR Bank Mandiri (Tier-2 SOP)
    b3_id = "bucket_juknis_operasional_kur"
    b3_dir = os.path.join(BUCKETS_BASE_DIR, b3_id)
    if not os.path.exists(b3_dir):
        os.makedirs(os.path.join(b3_dir, "documents"), exist_ok=True)
        sample_juknis_clauses = [
            {
                "id": "JUKNIS-01",
                "regulasi_terkait": "Petunjuk Teknis Operasional KUR Mandiri",
                "pasal_regulasi": "BAB III Ketentuan KUR",
                "topik": "Kriteria Kelayakan Usaha Produktif Calon Debitur KUR",
                "teks_regulasi": "Calon debitur penerima fasilitas KUR wajib memiliki usaha produktif dan layak dibiayai yang telah aktif beroperasi paling singkat 6 (enam) bulan dibuktikan dengan NIB atau SKU.",
            },
            {
                "id": "JUKNIS-02",
                "regulasi_terkait": "Petunjuk Teknis Operasional KUR Mandiri",
                "pasal_regulasi": "BAB III Ketentuan KUR - Bunga",
                "topik": "Penetapan Suku Bunga dan Marjin Pinjaman KUR",
                "teks_regulasi": "Suku bunga pinjaman KUR Mikro dan KUR Kecil ditetapkan flat 6% efektif per tahun untuk seluruh siklus pinjaman debitur.",
            },
            {
                "id": "JUKNIS-03",
                "regulasi_terkait": "Petunjuk Teknis Operasional KUR Mandiri",
                "pasal_regulasi": "BAB III Ketentuan KUR - Agunan",
                "topik": "Persyaratan Agunan Tambahan bagi Penerima KUR",
                "teks_regulasi": "Unit Bisnis Mikro Bank Mandiri wajib meminta agunan tambahan berupa sertifikat tanah/bangunan atau BPKB untuk permohonan pinjaman KUR di atas Rp 50.000.000.",
            },
            {
                "id": "JUKNIS-04",
                "regulasi_terkait": "Petunjuk Teknis Operasional KUR Mandiri",
                "pasal_regulasi": "BAB IV Prosedur Pelaksanaan",
                "topik": "Verifikasi Basis Data SIKP Kementerian Keuangan",
                "teks_regulasi": "Sebelum penerbitan SP3K, pejabat pemutus kredit wajib melakukan pemeriksaan status calon debitur pada Sistem Informasi Kredit Program SIKP Kementerian Keuangan.",
            },
        ]
        meta_3 = {
            "id": b3_id,
            "name": "Juknis Operasional KUR Bank Mandiri (Tier-2 SOP)",
            "category": "Petunjuk Teknis Lapangan",
            "description": "Petunjuk Teknis Operasional KUR (Edisi 8 MDAB): Tata cara penyaluran, kriteria debitur, bunga, agunan, dan verifikasi Sistem Informasi Kredit Program (SIKP).",
            "is_default": True,
            "files": ["Petunjuk_Teknis_Operasional_Kredit_Usaha_Rakyat_KUR_i3587.pdf"],
            "clauses": sample_juknis_clauses,
        }
        with open(os.path.join(b3_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta_3, f, indent=2, ensure_ascii=False)


def list_buckets() -> List[Dict[str, Any]]:
    """Mengembalikan daftar ringkasan seluruh bucket yang tersedia."""
    init_default_buckets()
    buckets = []
    for item in os.listdir(BUCKETS_BASE_DIR):
        item_path = os.path.join(BUCKETS_BASE_DIR, item)
        meta_file = os.path.join(item_path, "metadata.json")
        if os.path.isdir(item_path) and os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    buckets.append({
                        "id": meta["id"],
                        "name": meta["name"],
                        "category": meta.get("category", "Kustom"),
                        "description": meta.get("description", ""),
                        "is_default": meta.get("is_default", False),
                        "total_files": len(meta.get("files", [])),
                        "total_clauses": len(meta.get("clauses", [])),
                    })
            except Exception:
                continue
    return buckets


def get_bucket(bucket_id: str) -> Optional[Dict[str, Any]]:
    """Mengambil data lengkap satu bucket berdasarkan ID."""
    init_default_buckets()
    meta_file = os.path.join(BUCKETS_BASE_DIR, bucket_id, "metadata.json")
    if not os.path.exists(meta_file):
        return None
    with open(meta_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_bucket(name: str, description: str = "", category: str = "Koleksi Kustom") -> Dict[str, Any]:
    """Membuat bucket dokumen acuan baru."""
    init_default_buckets()
    slug = _slugify(name)
    bucket_id = f"bucket_{slug}" if not slug.startswith("bucket_") else slug
    
    # Hindari tabrakan ID
    counter = 1
    original_id = bucket_id
    while os.path.exists(os.path.join(BUCKETS_BASE_DIR, bucket_id)):
        bucket_id = f"{original_id}_{counter}"
        counter += 1

    bucket_dir = os.path.join(BUCKETS_BASE_DIR, bucket_id)
    os.makedirs(os.path.join(bucket_dir, "documents"), exist_ok=True)

    meta = {
        "id": bucket_id,
        "name": name.strip(),
        "category": category.strip(),
        "description": description.strip() or "Koleksi dokumen acuan khusus yang diunggah pengguna.",
        "is_default": False,
        "files": [],
        "clauses": [],
    }

    with open(os.path.join(bucket_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return meta


def add_document_to_bucket(bucket_id: str, file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Mengekstrak teks dokumen (PDF/DOCX), mem-parsing hierarki Bab/Pasal/Artikel,
    dan menyimpannya sebagai klausul acuan di dalam bucket terpilih.
    """
    bucket = get_bucket(bucket_id)
    if not bucket:
        raise ValueError(f"Bucket dengan ID '{bucket_id}' tidak ditemukan.")

    # Simpan berkas fisik ke folder documents di bucket
    bucket_dir = os.path.join(BUCKETS_BASE_DIR, bucket_id)
    doc_path = os.path.join(bucket_dir, "documents", filename)
    with open(doc_path, "wb") as f:
        f.write(file_bytes)

    # Ekstraksi dan parsing hierarki klausul
    raw_text = extract_raw_text(file_bytes, filename)
    parsed = parse_legal_structure(raw_text)

    new_clauses = []
    existing_count = len(bucket.get("clauses", []))

    for idx, c in enumerate(parsed.get("clauses", [])):
        clause_id = f"{bucket_id[:6].upper()}-{existing_count + idx + 1:03d}"
        new_clauses.append({
            "id": clause_id,
            "regulasi_terkait": parsed.get("title", filename),
            "pasal_regulasi": f"{c.get('bab', '')} ({c.get('pasal', '')})",
            "topik": f"{c.get('pasal', '')} {c.get('ayat', '')}: {c.get('text', '')[:70]}",
            "teks_regulasi": c.get("text", ""),
            "source_file": filename,
        })

    # Update metadata
    if filename not in bucket["files"]:
        bucket["files"].append(filename)
    bucket["clauses"].extend(new_clauses)

    meta_file = os.path.join(bucket_dir, "metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(bucket, f, indent=2, ensure_ascii=False)

    # Invalidate retriever cache untuk bucket ini
    if bucket_id in _RETRIEVER_CACHE:
        del _RETRIEVER_CACHE[bucket_id]

    return {
        "bucket_id": bucket_id,
        "filename": filename,
        "new_clauses_count": len(new_clauses),
        "total_clauses_count": len(bucket["clauses"]),
    }


def delete_bucket(bucket_id: str) -> bool:
    """Menghapus bucket kustom beserta dokumen di dalamnya (default bucket diproteksi)."""
    bucket = get_bucket(bucket_id)
    if not bucket:
        return False
    if bucket.get("is_default", False):
        raise PermissionError("Bucket bawaan sistem tidak dapat dihapus.")

    bucket_dir = os.path.join(BUCKETS_BASE_DIR, bucket_id)
    if os.path.exists(bucket_dir):
        shutil.rmtree(bucket_dir)

    if bucket_id in _RETRIEVER_CACHE:
        del _RETRIEVER_CACHE[bucket_id]

    return True


def get_bucket_retriever(bucket_id: str) -> SemanticRetriever:
    """Mengembalikan SemanticRetriever yang sudah terindeks terhadap klausul bucket ini."""
    if bucket_id in _RETRIEVER_CACHE:
        return _RETRIEVER_CACHE[bucket_id]

    bucket = get_bucket(bucket_id)
    clauses = bucket.get("clauses", []) if bucket else DEFAULT_REGULATORY_CORPUS
    if not clauses:
        clauses = DEFAULT_REGULATORY_CORPUS

    retriever = SemanticRetriever(clauses)
    _RETRIEVER_CACHE[bucket_id] = retriever
    return retriever
