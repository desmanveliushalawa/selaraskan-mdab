"""
Unit tests untuk engine/bucket_manager.py
"""

import os
import unittest
from engine.bucket_manager import (
    list_buckets,
    get_bucket,
    get_bucket_retriever,
    create_bucket,
    delete_bucket,
    add_document_to_bucket,
)


class TestBucketManager(unittest.TestCase):
    def test_list_and_get_default_buckets(self):
        buckets = list_buckets()
        self.assertGreaterEqual(len(buckets), 3)
        b_ids = [b["id"] for b in buckets]
        self.assertIn("bucket_regulasi_eksternal_ojk", b_ids)
        self.assertIn("bucket_kebijakan_kredit_mandiri", b_ids)
        self.assertIn("bucket_juknis_operasional_kur", b_ids)

        b1 = get_bucket("bucket_regulasi_eksternal_ojk")
        self.assertIsNotNone(b1)
        self.assertGreaterEqual(len(b1["clauses"]), 10)

    def test_get_bucket_retriever(self):
        retriever = get_bucket_retriever("bucket_regulasi_eksternal_ojk")
        matches = retriever.retrieve_best_match("suku bunga KUR mikro", top_k=1)
        self.assertEqual(len(matches), 1)
        self.assertIn("Permenko", matches[0]["regulasi_terkait"])

    def test_create_and_delete_custom_bucket(self):
        new_b = create_bucket(
            name="Bucket Unit Kepatuhan Khusus",
            description="Testing custom bucket creation",
            category="Kustom",
        )
        self.assertTrue(new_b["id"].startswith("bucket_"))

        # Verifikasi terdaftar
        b_list = list_buckets()
        ids = [b["id"] for b in b_list]
        self.assertIn(new_b["id"], ids)

        # Test add document text
        sample_txt = b"BAB I KETENTUAN\nPasal 1\n(1) Unit kerja wajib melakukan verifikasi internal berkala."
        res = add_document_to_bucket(new_b["id"], sample_txt, "aturan_internal.txt")
        self.assertGreater(res["new_clauses_count"], 0)

        # Delete
        success = delete_bucket(new_b["id"])
        self.assertTrue(success)

    def test_audit_document_against_bucket(self):
        from engine.alignment_engine import evaluate_custom_clause_alignment, calculate_compliance_metrics
        from engine.legal_parser import extract_raw_text, parse_legal_structure

        # Ambil berkas SOP KUR Mandiri
        doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dokumen_internal_mandiri", "SOP_Penyaluran_KUR_Bank_Mandiri.docx")
        self.assertTrue(os.path.exists(doc_path))

        with open(doc_path, "rb") as f:
            bytes_data = f.read()

        raw_text = extract_raw_text(bytes_data, "SOP_Penyaluran_KUR_Bank_Mandiri.docx")
        parsed = parse_legal_structure(raw_text)
        self.assertGreater(len(parsed["clauses"]), 0)

        # Audit terhadap Bucket Regulasi Eksternal (OJK, Permenko KUR)
        retriever = get_bucket_retriever("bucket_regulasi_eksternal_ojk")
        eval_list = []
        for c in parsed["clauses"]:
            matches = retriever.retrieve_best_match(c["text"], top_k=1)
            self.assertTrue(len(matches) > 0)
            ref_sample = matches[0]
            eval_res = evaluate_custom_clause_alignment(c["text"], ref_sample["teks_regulasi"])
            eval_list.append(eval_res)

        metrics = calculate_compliance_metrics(eval_list)
        self.assertEqual(metrics["total"], len(parsed["clauses"]))
        # Pastikan ada klausul yang terdeteksi tidak selaras (misal agunan KUR tambahan di bawah 100 juta)
        self.assertGreater(metrics["tidak_selaras"]["count"], 0)


if __name__ == "__main__":
    unittest.main()
