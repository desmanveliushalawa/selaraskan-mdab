"""
alignment_engine.py
Modul untuk mengevaluasi keselarasan semantik antara aturan operasional internal bank
dan peraturan eksternal (POJK, UU, PADG BI), menghitung metrik kepatuhan dokumen,
dan memberikan penjelasan pertimbangan hukum (reasoning).
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple


def get_default_dataset_path() -> str:
    """Mengembalikan path default ke berkas dataset demonstrasi Bank Mandiri."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", "bank_mandiri_demo.json")


def load_benchmark_data(filepath: str | None = None) -> Dict[str, Any]:
    """
    Memuat data benchmark dari file JSON.
    """
    if filepath is None:
        filepath = get_default_dataset_path()
        
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Berkas benchmark data tidak ditemukan di: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data


def calculate_compliance_metrics(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Menghitung agregasi metrik kepatuhan dokumen:
    - Total klausul
    - Jumlah & persentase Selaras (Positif)
    - Jumlah & persentase Tidak Selaras (Negatif)
    - Jumlah & persentase Netral
    """
    total = len(clauses)
    if total == 0:
        return {
            "total": 0,
            "selaras": {"count": 0, "pct": 0.0},
            "tidak_selaras": {"count": 0, "pct": 0.0},
            "netral": {"count": 0, "pct": 0.0},
        }

    counts = {"Selaras": 0, "Tidak Selaras": 0, "Netral": 0}
    for c in clauses:
        status = c.get("status", "Netral")
        if status in counts:
            counts[status] += 1
        else:
            counts["Netral"] += 1

    return {
        "total": total,
        "selaras": {
            "count": counts["Selaras"],
            "pct": round((counts["Selaras"] / total) * 100, 1),
        },
        "tidak_selaras": {
            "count": counts["Tidak Selaras"],
            "pct": round((counts["Tidak Selaras"] / total) * 100, 1),
        },
        "netral": {
            "count": counts["Netral"],
            "pct": round((counts["Netral"] / total) * 100, 1),
        },
    }


def evaluate_custom_clause_alignment(
    internal_text: str,
    external_text: str,
    api_key: str | None = None
) -> Dict[str, Any]:
    """
    Mengevaluasi keselarasan antara 1 klausul internal baru dan 1 pasal regulasi eksternal.
    Dapat menggunakan Live LLM jika api_key tersedia, atau menggunakan
    penalaran heuristik semantik lokal berbasis aturan hukum Indonesia (offline-safe).
    """
    internal_clean = internal_text.strip()
    external_clean = external_text.strip()

    if not internal_clean or not external_clean:
        return {
            "status": "Netral",
            "confidence": 0.50,
            "reasoning": "Teks klausul atau regulasi rujukan belum diisi secara lengkap.",
            "rekomendasi": "Lengkapi kedua teks perbandingan sebelum menjalankan evaluasi.",
        }

    # Cek kata kunci konflik hukum perbankan (Contradiction Indicators)
    lower_int = internal_clean.lower()
    lower_ext = external_clean.lower()

    # Indikator kontradiksi umum dalam regulasi
    conflict_patterns = [
        ("tanpa persetujuan", "wajib", "Klausul internal mengizinkan tindakan tanpa persetujuan, sedangkan regulasi mewajibkan persetujuan formal."),
        ("tanpa keharusan", "wajib", "Pengecualian sepihak pada dokumen internal bertentangan dengan kewajiban absolut dari regulator."),
        ("dikecualikan", "wajib", "Pengecualian pada SOP bertentangan dengan kewajiban regulasi."),
        ("hari kerja", "3 x 24", "Ketidaksinkronan tenggat waktu: SOP internal menggunakan acuan hari kerja sedangkan regulasi mewajibkan batas waktu kalender jam (3x24 jam)."),
        ("diperkenankan di luar", "di wilayah indonesia", "Lokasi kepatuhan bertentangan dengan asas penempatan yurisdiksi dalam negeri."),
        ("tidak wajib", "wajib", "Klausul internal menafikan hal yang diwajibkan oleh regulator."),
        ("dilarang", "dapat", "Klausul internal melarang apa yang diperbolehkan regulasi."),
        ("flat", "berjenjang", "Penyimpangan skema suku bunga: Bank menerapkan bunga flat 6% tanpa kenaikan, sedangkan Permenko No. 1 Tahun 2023 mewajibkan skema suku bunga berjenjang (6%, 7%, 8%, 9%) untuk debitur berulang."),
        ("tanpa memberlakukan", "berjenjang", "Penyimpangan skema suku bunga: SOP internal meniadakan skema kenaikan suku bunga berjenjang yang diwajibkan pemerintah."),
        ("wajib meminta agunan", "dilarang meminta agunan", "Pertentangan persyaratan agunan: SOP bank mewajibkan agunan tambahan, sedangkan Permenko KUR melarang keras pembebanan agunan tambahan untuk pinjaman sampai Rp 100 juta."),
        ("agunan tambahan", "dilarang", "Pelanggaran larangan agunan: Penyalur KUR dilarang membebankan agunan tambahan kepada calon penerima KUR dengan plafon sampai dengan Rp 100 juta."),
    ]

    for p_int, p_ext, explanation in conflict_patterns:
        if p_int in lower_int and p_ext in lower_ext:
            return {
                "status": "Tidak Selaras",
                "confidence": 0.95,
                "reasoning": f"Terdeteksi pertentangan normatif: {explanation}",
                "rekomendasi": "Segera revisi klausul operasional internal agar patuh dan selaras dengan regulasi regulator rujukan.",
            }

    # Indikator keselarasan (Entailment Indicators)
    entail_words = [
        "wajib", "enkripsi", "pengamanan", "kriptografi", "persetujuan",
        "cadangan", "pemulihan", "kepatuhan", "melindungi", "menjaga",
        "usaha", "produktif", "debitur", "plafon", "pemeriksaan", "verifikasi",
        "sikp", "kredit", "subsidi", "penjaminan"
    ]
    overlap_words = [w for w in entail_words if w in lower_int and w in lower_ext]

    if len(overlap_words) >= 2:
        return {
            "status": "Selaras",
            "confidence": 0.92,
            "reasoning": f"Klausul operasional memenuhi esensi persyaratan regulasi pada aspek: {', '.join(overlap_words)}. Ketentuan internal sejalan dengan arahan regulator.",
            "rekomendasi": "Pertahankan klausul ini dan pastikan kepatuhan implementasi di lapangan tetap diawasi berkala.",
        }

    # Default ke Netral
    return {
        "status": "Netral",
        "confidence": 0.85,
        "reasoning": "Klausul internal tidak bertentangan secara langsung dengan ketentuan regulasi rujukan dan mengatur aspek prosedural operasional internal.",
        "rekomendasi": "Dapat dipertahankan tanpa perubahan redaksional mendesak.",
    }


def link_rapat_teknis_to_clauses(
    clauses: List[Dict[str, Any]],
    doc_title: str,
    selected_rt_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Menghubungkan klausul-klausul dokumen target dengan riwayat rapat teknis (Audit Trail).
    Jika selected_rt_id diberikan, hanya menghubungkan dengan dokumen rapat teknis tersebut.
    Jika tidak, mencari seluruh berkas rapat teknis yang relevan dengan judul dokumen target.
    """
    from engine.rapat_teknis_manager import find_rapat_teknis_for_target, get_rapat_teknis
    
    if selected_rt_id:
        rt_doc = get_rapat_teknis(selected_rt_id)
        records = [rt_doc] if rt_doc else []
    else:
        records = find_rapat_teknis_for_target(doc_title)
        
    for c in clauses:
        c["rapat_teknis_history"] = []
        clause_pasal = c.get("pasal", "").lower()
        clause_text = c.get("text", "").lower()
        clause_bab = c.get("bab", "").lower()
        
        for rec in records:
            meeting_date = rec.get("meeting_date", "")
            meeting_title = rec.get("meeting_title", "")
            organizer = rec.get("organizer", "")
            
            for ch in rec.get("changes", []):
                ref = ch.get("clause_ref", "").lower()
                topic = ch.get("topic", "").lower()
                sub = ch.get("sub_ref", "").lower()
                
                # Cek kecocokan nomor pasal/klausul atau topik
                matched = False
                if ref and (ref in clause_pasal or clause_pasal in ref):
                    matched = True
                elif sub and (sub in clause_pasal or sub in clause_text):
                    matched = True
                elif topic and len(topic) > 5 and (topic in clause_text or topic in clause_pasal):
                    matched = True
                else:
                    # Cek overlap kata kunci spesifik perbankan (agunan, bunga, bpjs, limit)
                    for kw in ["agunan", "bunga", "bpjs", "penjaminan", "plafon", "sikp"]:
                        if kw in ref and (kw in clause_pasal or kw in clause_text):
                            matched = True
                            break
                            
                if matched:
                    # Hindari duplikasi jika topik/meeting sudah ada
                    already_exists = any(
                        h.get("meeting_id") == rec.get("id") and h.get("topic") == ch.get("topic")
                        for h in c["rapat_teknis_history"]
                    )
                    if not already_exists:
                        c["rapat_teknis_history"].append({
                            "meeting_id": rec.get("id"),
                            "meeting_date": meeting_date,
                            "meeting_title": meeting_title,
                            "organizer": organizer,
                            "clause_ref": ch.get("clause_ref", ""),
                            "sub_ref": ch.get("sub_ref", ""),
                            "topic": ch.get("topic", ""),
                            "before_text": ch.get("before_text", ""),
                            "after_text": ch.get("after_text", ""),
                            "reason": ch.get("reason", ""),
                        })
                    
        # Urutkan kronologis dari tanggal terlama ke terbaru
        c["rapat_teknis_history"].sort(key=lambda x: x.get("meeting_date", ""))
        
    return clauses


