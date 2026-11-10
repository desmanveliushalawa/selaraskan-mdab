"""
Unit tests untuk modul semantic_retriever.
"""
import unittest
from engine.semantic_retriever import SemanticRetriever, get_default_retriever


class TestSemanticRetriever(unittest.TestCase):
    def setUp(self):
        self.retriever = get_default_retriever()

    def test_retrieve_encryption_clause(self):
        query = "Bank wajib menerapkan enkripsi AES-256 pada media transmisi data nasabah."
        matches = self.retriever.retrieve_best_match(query, top_k=1)
        self.assertEqual(len(matches), 1)
        best = matches[0]
        self.assertEqual(best["id"], "REG-01")
        self.assertIn("kriptografi", best["teks_regulasi"].lower())
        self.assertGreater(best["similarity_score"], 0.15)

    def test_retrieve_breach_clause(self):
        query = "Laporan insiden kegagalan kebocoran data wajib disampaikan maksimal 7 hari kerja."
        matches = self.retriever.retrieve_best_match(query, top_k=1)
        self.assertEqual(len(matches), 1)
        best = matches[0]
        self.assertEqual(best["id"], "REG-02")
        self.assertIn("UU PDP", best["regulasi_terkait"])

    def test_retrieve_cloud_datacenter_clause(self):
        query = "Penyimpanan data transaksi pada server cloud di luar negeri."
        matches = self.retriever.retrieve_best_match(query, top_k=1)
        self.assertEqual(len(matches), 1)
        best = matches[0]
        self.assertEqual(best["id"], "REG-04")
        self.assertIn("wilayah Indonesia", best["teks_regulasi"])


if __name__ == "__main__":
    unittest.main()
