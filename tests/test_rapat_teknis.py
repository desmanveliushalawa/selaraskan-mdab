"""
Unit tests untuk modul rapat_teknis_manager, rapat_teknis_parser, dan linking engine.
"""

import io
import os
import sys
import unittest
import docx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.rapat_teknis_manager import (
    list_rapat_teknis,
    get_rapat_teknis,
    save_rapat_teknis,
    delete_rapat_teknis,
    find_rapat_teknis_for_target,
    init_default_rapat_teknis,
)
from engine.rapat_teknis_parser import (
    parse_rapat_teknis_docx,
    parse_rapat_teknis_csv,
    parse_rapat_teknis_file,
)
from engine.alignment_engine import link_rapat_teknis_to_clauses


class TestRapatTeknis(unittest.TestCase):
    def setUp(self):
        init_default_rapat_teknis()

    def test_list_and_get_default_rapat_teknis(self):
        records = list_rapat_teknis()
        self.assertGreaterEqual(len(records), 1)
        
        default_rec = records[0]
        self.assertIn("target_doc_id", default_rec)
        self.assertIn("meeting_date", default_rec)
        
        full_rec = get_rapat_teknis(default_rec["id"])
        self.assertIsNotNone(full_rec)
        self.assertIn("changes", full_rec)
        self.assertGreaterEqual(len(full_rec["changes"]), 1)

    def test_find_rapat_teknis_for_target(self):
        target_title = "Petunjuk Teknis Operasional Kredit Usaha Rakyat (KUR) 2026"
        matched = find_rapat_teknis_for_target(target_title)
        self.assertGreaterEqual(len(matched), 1)
        self.assertIn("KUR", matched[0]["target_doc_id"])

    def test_save_and_delete_rapat_teknis(self):
        custom_data = {
            "id": "rt_test_custom_001",
            "target_doc_id": "Standar Operasional Prosedur Pengkreditan Mikro",
            "meeting_date": "2026-02-15",
            "meeting_title": "Rapat Teknis Pembahasan NPL Mikro",
            "organizer": "SMR Group",
            "notes": "Testing unit test",
            "changes": [
                {
                    "clause_ref": "Pasal 5 NPL",
                    "before_text": "Toleransi NPL 5%",
                    "after_text": "Toleransi NPL 3%",
                    "reason": "Pengetatan manajemen risiko",
                }
            ],
        }
        saved = save_rapat_teknis(custom_data)
        self.assertEqual(saved["id"], "rt_test_custom_001")
        
        fetched = get_rapat_teknis("rt_test_custom_001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["meeting_title"], "Rapat Teknis Pembahasan NPL Mikro")
        
        deleted = delete_rapat_teknis("rt_test_custom_001")
        self.assertTrue(deleted)
        self.assertIsNone(get_rapat_teknis("rt_test_custom_001"))

    def test_parse_rapat_teknis_csv(self):
        csv_content = (
            "No,Klausul,Sebelum,Sesudah,Alasan\n"
            "1,H. Agunan,Wajib agunan tanah,Dilarang agunan tambahan,Sesuai Permenko 1/2026\n"
            "2,Bunga,Flat 6%,Berjenjang 6-9%,Graduasi debitur\n"
        ).encode("utf-8")
        
        changes = parse_rapat_teknis_csv(csv_content)
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0]["clause_ref"], "H. Agunan")
        self.assertIn("Wajib agunan", changes[0]["before_text"])
        self.assertIn("Dilarang agunan", changes[0]["after_text"])
        self.assertIn("Permenko", changes[0]["reason"])

    def test_parse_rapat_teknis_docx(self):
        doc = docx.Document()
        table = doc.add_table(rows=2, cols=4)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Pasal / Ketentuan"
        hdr_cells[1].text = "Semula / Sebelum"
        hdr_cells[2].text = "Menjadi / Sesudah"
        hdr_cells[3].text = "Alasan Perubahan"
        
        row_cells = table.rows[1].cells
        row_cells[0].text = "Pasal 10 Bunga"
        row_cells[1].text = "Bunga flat 6% per tahun"
        row_cells[2].text = "Bunga berjenjang 6% s.d 9%"
        row_cells[3].text = "Penyesuaian Permenko 1/2026"
        
        buffer = io.BytesIO()
        doc.save(buffer)
        
        changes = parse_rapat_teknis_docx(buffer.getvalue())
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["clause_ref"], "Pasal 10 Bunga")
        self.assertIn("flat 6%", changes[0]["before_text"])
        self.assertIn("berjenjang", changes[0]["after_text"])

    def test_link_rapat_teknis_to_clauses(self):
        sample_clauses = [
            {
                "bab": "BAB III : KETENTUAN KUR",
                "pasal": "H. Agunan",
                "ayat": "2. Agunan Tambahan",
                "text": "KUR dengan limit kredit sampai dengan Rp 100.000.000 dilarang agunan tambahan.",
            },
            {
                "bab": "BAB I : PENDAHULUAN",
                "pasal": "A. Latar Belakang",
                "ayat": "Klausul Utama",
                "text": "Kredit Usaha Rakyat merupakan program prioritas pemerintah.",
            },
        ]
        
        linked = link_rapat_teknis_to_clauses(
            sample_clauses,
            doc_title="Petunjuk Teknis Operasional Kredit Usaha Rakyat (KUR) 2026",
        )
        
        # Klausul Agunan harus punya riwayat rapat teknis
        agunan_clause = linked[0]
        self.assertIn("rapat_teknis_history", agunan_clause)
        self.assertGreaterEqual(len(agunan_clause["rapat_teknis_history"]), 1)
        history_item = agunan_clause["rapat_teknis_history"][0]
        self.assertEqual(history_item["meeting_date"], "2026-01-13")
        self.assertIn("Permenko", history_item["reason"])
        
        # Klausul Latar Belakang tidak punya riwayat perubahan
        bg_clause = linked[1]
        self.assertEqual(len(bg_clause["rapat_teknis_history"]), 0)


if __name__ == "__main__":
    unittest.main()
