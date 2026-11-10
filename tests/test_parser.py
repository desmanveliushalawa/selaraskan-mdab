"""
Unit tests untuk modul legal_parser.
"""
import io
import unittest
import docx
from engine.legal_parser import extract_raw_text, parse_legal_structure


class TestLegalParser(unittest.TestCase):
    def test_parse_legal_structure_sample(self):
        sample_doc = """
        PETUNJUK OPERASIONAL TATA KELOLA TEKNOLOGI INFORMASI
        
        BAB I KETENTUAN UMUM
        Pasal 1
        (1) Bank wajib mengelola sistem informasi secara andal.
        (2) Seluruh operasional diawasi oleh komite risiko.
        
        BAB II PENGAMANAN DATA
        Pasal 2
        (1) Data nasabah wajib dienkripsi saat transit.
        (2) Data nasabah wajib dienkripsi saat penyimpanan.
        
        Pasal 3
        Pusat data pemulihan bencana wajib diuji setahun sekali.
        """
        
        result = parse_legal_structure(sample_doc)
        self.assertIn("PETUNJUK OPERASIONAL", result["title"])
        self.assertEqual(result["total_bab"], 2)
        self.assertEqual(result["total_pasal"], 3)
        self.assertEqual(result["total_ayat"], 5)
        self.assertEqual(len(result["clauses"]), 5)
        
        first_clause = result["clauses"][0]
        self.assertIn("BAB I", first_clause["bab"])
        self.assertEqual(first_clause["pasal"], "Pasal 1")
        self.assertEqual(first_clause["ayat"], "Ayat (1)")
        self.assertIn("Bank wajib mengelola", first_clause["text"])

    def test_extract_raw_text_txt(self):
        raw_bytes = "Pasal 1 Ketentuan Umum".encode("utf-8")
        text = extract_raw_text(raw_bytes, "aturan.txt")
        self.assertEqual(text, "Pasal 1 Ketentuan Umum")

    def test_extract_raw_text_docx(self):
        doc = docx.Document()
        doc.add_paragraph("BAB I PENDAHULUAN")
        doc.add_paragraph("Pasal 1 Definisi")
        buffer = io.BytesIO()
        doc.save(buffer)
        
        text = extract_raw_text(buffer.getvalue(), "dokumen.docx")
        self.assertIn("BAB I PENDAHULUAN", text)
        self.assertIn("Pasal 1 Definisi", text)


if __name__ == "__main__":
    unittest.main()

