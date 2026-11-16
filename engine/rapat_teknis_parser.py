"""
rapat_teknis_parser.py
Modul parser untuk mengekstrak berkas Matriks Perubahan / Notulen Rapat Teknis (DOCX, CSV, JSON).
Menghasilkan daftar perubahan klausul terstruktur (clause_ref, before_text, after_text, reason).
"""

import csv
import io
import json
import os
import re
from typing import Any, Dict, List, Tuple
import docx


def parse_rapat_teknis_docx(file_bytes: bytes) -> List[Dict[str, str]]:
    """
    Mengekstrak tabel matriks perubahan dari dokumen Microsoft Word (.docx).
    Mengenali tabel dengan kolom: Klausul/Pasal, Sebelum/Lama, Sesudah/Baru, Alasan/Catatan.
    """
    doc = docx.Document(io.BytesIO(file_bytes))
    changes: List[Dict[str, str]] = []

    for table in doc.tables:
        if len(table.rows) < 2:
            continue

        header_cells = [c.text.strip().lower() for c in table.rows[0].cells]
        col_clause = -1
        col_before = -1
        col_after = -1
        col_reason = -1
        col_topic = -1

        for idx, text in enumerate(header_cells):
            if any(k in text for k in ["klausul", "pasal", "ketentuan", "bagian", "butir"]):
                col_clause = idx
            elif any(k in text for k in ["sebelum", "lama", "eksisting", "before", "semula"]):
                col_before = idx
            elif any(k in text for k in ["sesudah", "baru", "usulan", "after", "revisi"]):
                col_after = idx
            elif any(k in text for k in ["alasan", "keterangan", "catatan", "dasar", "justifikasi", "reason"]):
                col_reason = idx
            elif any(k in text for k in ["topik", "subjek", "perihal", "judul"]):
                col_topic = idx

        # Jika kolom sebelum dan sesudah teridentifikasi
        if col_before != -1 and col_after != -1:
            for row in table.rows[1:]:
                cells = [c.text.strip() for c in row.cells]
                before_t = cells[col_before] if col_before < len(cells) else ""
                after_t = cells[col_after] if col_after < len(cells) else ""
                
                # Lewati baris kosong
                if not before_t and not after_t:
                    continue

                clause_ref = cells[col_clause] if col_clause != -1 and col_clause < len(cells) else "Ketentuan Terkait"
                reason_t = cells[col_reason] if col_reason != -1 and col_reason < len(cells) else "Penyesuaian hasil rapat teknis."
                topic_t = cells[col_topic] if col_topic != -1 and col_topic < len(cells) else clause_ref

                changes.append({
                    "clause_ref": clause_ref,
                    "sub_ref": "",
                    "topic": topic_t,
                    "before_text": before_t,
                    "after_text": after_t,
                    "reason": reason_t,
                })

    return changes


def parse_rapat_teknis_csv(file_bytes: bytes) -> List[Dict[str, str]]:
    """Mengekstrak berkas matriks perubahan format CSV."""
    text_content = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text_content))
    rows = list(reader)
    if len(rows) < 2:
        return []

    header = [h.strip().lower() for h in rows[0]]
    col_clause = -1
    col_before = -1
    col_after = -1
    col_reason = -1
    col_topic = -1

    for idx, text in enumerate(header):
        if any(k in text for k in ["klausul", "pasal", "ketentuan", "bagian"]):
            col_clause = idx
        elif any(k in text for k in ["sebelum", "lama", "before", "semula"]):
            col_before = idx
        elif any(k in text for k in ["sesudah", "baru", "after", "revisi"]):
            col_after = idx
        elif any(k in text for k in ["alasan", "keterangan", "catatan", "reason"]):
            col_reason = idx
        elif any(k in text for k in ["topik", "judul", "perihal"]):
            col_topic = idx

    changes: List[Dict[str, str]] = []
    if col_before != -1 and col_after != -1:
        for r in rows[1:]:
            if len(r) <= max(col_before, col_after):
                continue
            before_t = r[col_before].strip()
            after_t = r[col_after].strip()
            if not before_t and not after_t:
                continue

            clause_ref = r[col_clause].strip() if col_clause != -1 and col_clause < len(r) else "Ketentuan Terkait"
            reason_t = r[col_reason].strip() if col_reason != -1 and col_reason < len(r) else "Penyesuaian hasil rapat teknis."
            topic_t = r[col_topic].strip() if col_topic != -1 and col_topic < len(r) else clause_ref

            changes.append({
                "clause_ref": clause_ref,
                "sub_ref": "",
                "topic": topic_t,
                "before_text": before_t,
                "after_text": after_t,
                "reason": reason_t,
            })

    return changes


def parse_rapat_teknis_file(file_bytes: bytes, file_name: str) -> List[Dict[str, str]]:
    """Router fungsi untuk memproses aneka format berkas matriks perubahan."""
    ext = file_name.split(".")[-1].lower() if "." in file_name else ""
    if ext == "docx":
        return parse_rapat_teknis_docx(file_bytes)
    elif ext in ["csv", "txt"]:
        return parse_rapat_teknis_csv(file_bytes)
    elif ext == "json":
        try:
            data = json.loads(file_bytes.decode("utf-8-sig"))
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "changes" in data:
                return data["changes"]
        except Exception:
            return []
    return []
