"""
Script untuk mengekstrak dan mengekspor hasil parsing regulasi dan dokumen internal ke CSV.
1. PermenkoEkon No. 1 Tahun 2026.pdf (Regulasi Pemerintah)
2. Petunjuk Teknis Operasional Kredit Usaha Rakyat (KUR) i3587.pdf (PTO Bank Mandiri)
"""

import csv
import os
import sys
from engine.legal_parser import extract_raw_text, parse_legal_structure

def export_document_to_csv(pdf_path: str, output_csv_path: str, doc_label: str):
    print(f"[{doc_label}] Membaca berkas: {pdf_path}...")
    if not os.path.exists(pdf_path):
        print(f"ERROR: File {pdf_path} tidak ditemukan.")
        return False
    
    with open(pdf_path, "rb") as f:
        raw_bytes = f.read()
    
    print(f"[{doc_label}] Mengekstrak teks dari PDF...")
    text = extract_raw_text(raw_bytes, os.path.basename(pdf_path))
    
    print(f"[{doc_label}] Memparsing struktur hukum...")
    res = parse_legal_structure(text)
    
    clauses = res.get("clauses", [])
    print(f"[{doc_label}] Berhasil diekstrak:")
    print(f"  - Judul: {res.get('title')}")
    print(f"  - Total Bab: {res.get('total_bab')}")
    print(f"  - Total Pasal / Bagian: {res.get('total_pasal')}")
    print(f"  - Total Klausul: {len(clauses)}")
    
    with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["No", "Bab", "Pasal / Bagian", "Ayat / Butir", "Teks Klausul"])
        for idx, clause in enumerate(clauses, 1):
            writer.writerow([
                idx,
                clause.get("bab", ""),
                clause.get("pasal", ""),
                clause.get("ayat", ""),
                clause.get("text", "")
            ])
            
    print(f"[{doc_label}] File CSV berhasil disimpan ke: {output_csv_path} ({len(clauses)} baris)\n")
    return True

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # 1. Dokumen Peraturan Pemerintah: Permenko Perekonomian No. 1 Tahun 2026
    permenko_pdf = os.path.join(base_dir, "PermenkoEkon No. 1 Tahun 2026.pdf")
    permenko_csv = os.path.join(base_dir, "hasil_parsing_permenko_ekon_no_1_tahun_2026.csv")
    export_document_to_csv(permenko_pdf, permenko_csv, "PERMENKO 2026")
    
    # 2. Dokumen Internal: PTO KUR Bank Mandiri Edisi 8
    pto_pdf = os.path.join(base_dir, "data", "Petunjuk Teknis Operasional Kredit Usaha Rakyat (KUR) i3587.pdf")
    pto_csv = os.path.join(base_dir, "hasil_parsing_pto_kur_mandiri_edisi_8.csv")
    export_document_to_csv(pto_pdf, pto_csv, "PTO KUR MANDIRI")
    
    print("Semua proses ekspor selesai dengan sukses.")

