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
    for idx, line in enumerate(lines[:12]):
        u = line.upper()
        if any(term in u for term in ["DILARANG", "PERINTAH", "MEMPERBANYAK"]):
            continue
        if any(term in u for term in ["PETUNJUK", "PERATURAN", "SURAT EDARAN", "STANDAR OPERASIONAL", "PEDOMAN", "KEBIJAKAN", "UNDANG-UNDANG"]):
            if u != "UNDANG-UNDANG":
                cand = line
                if idx + 1 < len(lines) and len(lines[idx + 1]) < 60 and not any(k in lines[idx + 1].upper() for k in ["EDISI", "202", "BAB", "PASAL"]):
                    cand += " " + lines[idx + 1]
                title_candidates.append(cand)
                break
    doc_title = title_candidates[0] if title_candidates else lines[0][:80]

    clauses: List[Dict[str, Any]] = []
    current_bab = "Ketentuan Umum"
    current_pasal = ""
    current_pasal_lines: List[str] = []
    in_daftar_isi = False

    # Pola reguler untuk Bab, Bagian, Pasal, dan Sub-bab operasional
    bab_regex = re.compile(r"^(BAB\s+[IVXLCDM\d]+|BAGIAN\s+[IVXLCDM\d]+)(.*)$", re.IGNORECASE)
    pasal_regex = re.compile(r"^(Pasal\s+\d+|Artikel\s+\d+)(.*)$", re.IGNORECASE)
    subbab_regex = re.compile(r"^([A-Z]\.\s+[A-Za-z0-9].*)$")
    point_regex = re.compile(r"^(\d+\.\s+[A-Z][A-Za-z0-9\s/()-]+)$")
    ayat_start_regex = re.compile(r"^\((\d+)\)\s*(.*)$")

    def is_noise_line(line_str: str) -> bool:
        u = line_str.upper()
        if any(h in u for h in [
            "DILARANG MEMPERBANYAK",
            "TANPA PERSETUJUAN TERTULIS",
            "KARENA PERINTAH UNDANG-UNDANG",
            "PERINTAH UNDANG -UNDANG",
            "PETUNJUK TEKNIS OPERASIONAL KREDIT USAHA RAKYAT",
            "EDISI",
            "REVISI KE",
            "BERLAKU SEJAK TANGGAL",
            "TANGGAL YANG DIGANTIKAN",
        ]):
            return True
        if re.match(r"^BANK MANDIRI(\s+\d+)?$", u):
            return True
        if re.match(r"^\d+\s*-\s*\d{2}/\d{2}/\d{4}", u):
            return True
        if re.match(r"^HALAMAN\s+\d+(\s+DARI\s+\d+)?$", u):
            return True
        if re.match(r"^-\s*\d+\s*-$", line_str):
            return True
        if re.match(r"^:\s*\d+", line_str) or re.match(r"^:\s*\d+\s+[A-Za-z]+", line_str):
            return True
        if re.match(r"^[IVXLCDM\d]+\s*-\s*\d+$", line_str):
            return True
        if re.search(r"\b\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\b", line_str):
            return True
        return False

    def parse_external(lines_to_parse: List[str]) -> List[Dict[str, Any]]:
        extracted: List[Dict[str, Any]] = []
        cur_bab = "Ketentuan Umum"
        cur_pasal = ""
        cur_ayat = ""
        cur_lines: List[str] = []

        def flush():
            nonlocal cur_lines, cur_ayat
            if cur_pasal and cur_lines:
                body = " ".join(cur_lines).strip()
                if len(body) > 10:
                    extracted.append({
                        "bab": cur_bab,
                        "pasal": cur_pasal,
                        "ayat": cur_ayat if cur_ayat else "Klausul Utama",
                        "text": body,
                    })
            cur_lines = []

        for line in lines_to_parse:
            if is_noise_line(line):
                continue

            m_bab = bab_regex.match(line)
            if m_bab:
                flush()
                bab_id = m_bab.group(1).upper()
                bab_desc = m_bab.group(2).strip(" -:.")
                cur_bab = f"{bab_id} : {bab_desc}" if bab_desc else bab_id
                cur_pasal = ""
                cur_ayat = ""
                continue

            m_pasal = pasal_regex.match(line)
            if m_pasal:
                flush()
                cur_pasal = m_pasal.group(1).title()
                cur_ayat = ""
                rem = m_pasal.group(2).strip(" -:.")
                if rem:
                    m_ay = ayat_start_regex.match(rem)
                    if m_ay:
                        cur_ayat = f"Ayat ({m_ay.group(1)})"
                        if m_ay.group(2):
                            cur_lines.append(m_ay.group(2))
                    else:
                        cur_lines.append(rem)
                continue

            if cur_pasal:
                m_ay = ayat_start_regex.match(line)
                if m_ay:
                    flush()
                    cur_ayat = f"Ayat ({m_ay.group(1)})"
                    if m_ay.group(2):
                        cur_lines.append(m_ay.group(2))
                    continue
                cur_lines.append(line)

        flush()
        return extracted

    def parse_internal(lines_to_parse: List[str]) -> List[Dict[str, Any]]:
        extracted: List[Dict[str, Any]] = []
        cur_bab = "Ketentuan Umum"
        cur_section = ""
        cur_item = ""
        cur_lines: List[str] = []
        in_toc = False

        def flush():
            nonlocal cur_lines
            if cur_section and cur_lines:
                body = " ".join(cur_lines).strip()
                if len(body) > 15:
                    extracted.append({
                        "bab": cur_bab,
                        "pasal": cur_section,
                        "ayat": cur_item if cur_item else "Ketentuan Pokok",
                        "text": body,
                    })
            cur_lines = []

        for line in lines_to_parse:
            if is_noise_line(line):
                continue

            if "DAFTAR ISI" in line.upper():
                in_toc = True
                continue

            m_bab = bab_regex.match(line)
            if m_bab:
                in_toc = False
                bab_id = m_bab.group(1).upper()
                bab_desc = m_bab.group(2).strip(" -:.")
                new_bab = f"{bab_id} : {bab_desc}" if bab_desc else bab_id
                if new_bab != cur_bab:
                    flush()
                    cur_bab = new_bab
                    cur_section = ""
                    cur_item = ""
                continue

            if in_toc:
                continue

            m_pasal = pasal_regex.match(line)
            if m_pasal:
                flush()
                cur_section = m_pasal.group(1).title()
                cur_item = "Klausul Utama"
                rem = m_pasal.group(2).strip(" -:.")
                if rem:
                    cur_lines.append(rem)
                continue

            m_sub = subbab_regex.match(line)
            if m_sub and len(line) < 100 and not line.endswith(":"):
                flush()
                cur_section = line.strip()
                cur_item = ""
                continue

            m_pt = point_regex.match(line)
            if m_pt and len(line) < 80 and not line.endswith(":"):
                flush()
                cur_item = line.strip()
                continue

            if cur_section:
                cur_lines.append(line)

        flush()
        return extracted

    # Deteksi strategi parsing: apakah dokumen regulasi eksternal (UU/Permenko/POJK) atau kebijakan internal (PTO/SOP)
    subbab_count = len(re.findall(r"^\s*[A-Z]\.\s+[A-Za-z0-9]", text, re.MULTILINE))
    pasal_count = len(re.findall(r"^\s*(Pasal|Artikel)\s+\d+", text, re.MULTILINE | re.IGNORECASE))

    if subbab_count > pasal_count:
        clauses = parse_internal(lines)
    else:
        clauses = parse_external(lines)

    # Fallback untuk dokumen kebijakan/RIPLAY/Pedoman operasional yang tidak menggunakan format Bab-Pasal formal
    if not clauses and len(lines) > 2:
        current_section = "Ketentuan Pokok"
        item_counter = 1

        for line in lines[1:]:
            if any(skip in line.upper() for skip in ["BERIZIN DAN DIAWASI", "NAMA PENERBIT", "JENIS PRODUK", "VERSI UMUM"]):
                continue
            if (line.isupper() and len(line) < 45 and not line.startswith("•")) or re.match(r"^[A-Z\d]\.\s+", line):
                current_section = line.strip(" :.-")
                continue
            if line.startswith("•") or line.startswith("-") or re.match(r"^\d+\.\s+", line):
                clean_item = re.sub(r"^[•\-\d\.\s]+", "", line).strip()
                if len(clean_item) > 10:
                    clauses.append({
                        "bab": current_section,
                        "pasal": f"Butir {item_counter}",
                        "ayat": "Ketentuan",
                        "text": clean_item,
                    })
                    item_counter += 1
            elif len(line) > 35 and not line.startswith("•"):
                clauses.append({
                    "bab": current_section,
                    "pasal": f"Butir {item_counter}",
                    "ayat": "Ketentuan",
                    "text": line,
                })
                item_counter += 1

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

