"""
legal_parser.py
Modul ekstraksi dan parsing hierarki dokumen hukum Indonesia (Word .docx, PDF, dan teks)
Mengekstrak struktur Bab, Pasal, Ayat, dan Angka secara otomatis.
"""

import io
import re
from typing import Any, Dict, List


def extract_raw_text(file_bytes: bytes, filename: str) -> str:
    """
    Mengekstrak teks mentah dari berkas DOCX, PDF, atau TXT.
    """
    ext = filename.lower().split(".")[-1]
    
    if ext == "docx":
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
        
    elif ext == "pdf":
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
        
    elif ext in ("txt", "json"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="ignore")
            
    else:
        raise ValueError(f"Format berkas .{ext} tidak didukung. Harap gunakan format .docx, .pdf, atau .txt")


def parse_legal_structure(text: str) -> Dict[str, Any]:
    """
    Mem-parsing teks regulasi Indonesia menjadi struktur hierarki Bab, Pasal, dan Ayat.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return {
            "title": "Dokumen Kosong",
            "total_bab": 0,
            "total_pasal": 0,
            "total_ayat": 0,
            "clauses": [],
        }

    # Deteksi judul dokumen dari baris awal
    title_candidates = []
    for line in lines[:8]:
        if any(term in line.upper() for term in ["PETUNJUK", "PERATURAN", "SURAT EDARAN", "STANDAR OPERASIONAL", "PEDOMAN", "UNDANG-UNDANG"]):
            title_candidates.append(line)
            break
    doc_title = title_candidates[0] if title_candidates else lines[0][:80]

    clauses: List[Dict[str, Any]] = []
    current_bab = "Ketentuan Umum"
    current_pasal = ""
    current_pasal_lines: List[str] = []

    # Pola reguler untuk Bab dan Pasal Indonesia
    bab_regex = re.compile(r"^(BAB\s+[IVXLCDM\d]+)(.*)$", re.IGNORECASE)
    pasal_regex = re.compile(r"^(Pasal\s+\d+)(.*)$", re.IGNORECASE)

    def flush_pasal():
        nonlocal current_pasal, current_pasal_lines
        if current_pasal and current_pasal_lines:
            pasal_body = " ".join(current_pasal_lines).strip()
            
            # Deteksi apakah di dalam pasal terdapat ayat terpisah
            ayat_matches = re.findall(r"(\(\d+\))\s*([^\(\)]+)", pasal_body)
            if ayat_matches:
                for ayat_num, ayat_content in ayat_matches:
                    clauses.append({
                        "bab": current_bab,
                        "pasal": current_pasal,
                        "ayat": f"Ayat {ayat_num}",
                        "text": ayat_content.strip(),
                    })
            else:
                clauses.append({
                    "bab": current_bab,
                    "pasal": current_pasal,
                    "ayat": "Klausul Utama",
                    "text": pasal_body,
                })
        current_pasal_lines = []

    for line in lines:
        match_bab = bab_regex.match(line)
        if match_bab:
            flush_pasal()
            bab_id = match_bab.group(1).upper()
            bab_desc = match_bab.group(2).strip(" -:.")
            current_bab = f"{bab_id} : {bab_desc}" if bab_desc else bab_id
            current_pasal = ""
            continue

        match_pasal = pasal_regex.match(line)
        if match_pasal:
            flush_pasal()
            current_pasal = match_pasal.group(1).capitalize()
            remainder = match_pasal.group(2).strip(" -:.")
            if remainder:
                current_pasal_lines.append(remainder)
            continue

        if current_pasal:
            current_pasal_lines.append(line)
        else:
            # Teks sebelum pasal pertama (misal bagian menimbang atau pendahuluan)
            pass

    flush_pasal()

    # Hitung jumlah unik Bab dan Pasal
    unique_babs = set(c["bab"] for c in clauses)
    unique_pasals = set(f"{c['bab']}_{c['pasal']}" for c in clauses)

    return {
        "title": doc_title,
        "total_bab": len(unique_babs),
        "total_pasal": len(unique_pasals),
        "total_ayat": len(clauses),
        "clauses": clauses,
    }

