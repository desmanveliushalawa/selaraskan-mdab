"""
Unit tests untuk modul engine (diff_highlighter dan alignment_engine).
"""
import unittest
from engine.diff_highlighter import tokenize_words, compute_word_diff, render_side_by_side_diff_html
from engine.alignment_engine import (
    load_benchmark_data,
    calculate_compliance_metrics,
    evaluate_custom_clause_alignment,
)


class TestDiffHighlighter(unittest.TestCase):
    def test_tokenize_words(self):
        text = "Pasal 4 Ayat (1) wajib dienkripsi."
        tokens = tokenize_words(text)
        self.assertIn("Pasal", tokens)
        self.assertIn("dienkripsi", tokens)
        self.assertEqual("".join(tokens), text)

    def test_compute_word_diff_identical(self):
        text = "Bank wajib menjaga kerahasiaan."
        diff_a, diff_b = compute_word_diff(text, text)
        self.assertNotIn("background-color", diff_a)
        self.assertNotIn("background-color", diff_b)

    def test_compute_word_diff_replacement(self):
        text_a = "lapor 7 hari kerja"
        text_b = "lapor 3 x 24 jam"
        diff_a, diff_b = compute_word_diff(text_a, text_b)
        self.assertIn("#ffebee", diff_a)  # Highlight merah
        self.assertIn("#e8f5e9", diff_b)  # Highlight hijau

    def test_render_side_by_side_diff_html(self):
        html = render_side_by_side_diff_html(
            title_internal="SOP Mandiri",
            text_internal="Tenggat waktu 7 hari kerja.",
            title_regulasi="UU PDP",
            text_regulasi="Tenggat waktu 3 x 24 jam.",
            status="Tidak Selaras",
            reasoning="Terdapat perbedaan tenggat waktu."
        )
        self.assertIn("KALIMAT INTERNAL BANK", html)
        self.assertIn("KALIMAT REGULASI PEMERINTAH", html)
        self.assertIn("Tidak Selaras", html)
        self.assertIn("Catatan Analisis Hukum", html)


class TestAlignmentEngine(unittest.TestCase):
    def test_load_benchmark_data(self):
        data = load_benchmark_data()
        self.assertIn("internal_document", data)
        self.assertIn("clauses", data)
        self.assertGreaterEqual(len(data["clauses"]), 6)

    def test_calculate_compliance_metrics(self):
        clauses = [
            {"status": "Selaras"},
            {"status": "Selaras"},
            {"status": "Tidak Selaras"},
            {"status": "Netral"},
        ]
        metrics = calculate_compliance_metrics(clauses)
        self.assertEqual(metrics["total"], 4)
        self.assertEqual(metrics["selaras"]["count"], 2)
        self.assertEqual(metrics["selaras"]["pct"], 50.0)
        self.assertEqual(metrics["tidak_selaras"]["count"], 1)
        self.assertEqual(metrics["tidak_selaras"]["pct"], 25.0)
        self.assertEqual(metrics["netral"]["count"], 1)
        self.assertEqual(metrics["netral"]["pct"], 25.0)

    def test_evaluate_custom_clause_conflict(self):
        internal = "Unit kerja diperkenankan mengoperasikan sistem tanpa persetujuan regulator."
        regulasi = "Bank wajib memperoleh persetujuan OJK terlebih dahulu."
        result = evaluate_custom_clause_alignment(internal, regulasi)
        self.assertEqual(result["status"], "Tidak Selaras")
        self.assertGreater(result["confidence"], 0.8)

    def test_evaluate_custom_clause_selaras(self):
        internal = "Bank wajib menerapkan enkripsi data dan pengamanan kriptografi nasabah."
        regulasi = "Bank wajib melakukan pengamanan enkripsi kriptografi data rahasia."
        result = evaluate_custom_clause_alignment(internal, regulasi)
        self.assertEqual(result["status"], "Selaras")


if __name__ == "__main__":
    unittest.main()
