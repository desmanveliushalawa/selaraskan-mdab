"""
Unit tests untuk modul report_generator (pembuatan PDF resmi).
"""
import unittest
from engine.alignment_engine import load_benchmark_data, calculate_compliance_metrics
from engine.report_generator import generate_compliance_pdf_report


class TestReportGenerator(unittest.TestCase):
    def test_generate_compliance_pdf_report(self):
        data = load_benchmark_data()
        metrics = calculate_compliance_metrics(data["clauses"])
        
        pdf_bytes = generate_compliance_pdf_report(
            doc_info=data["internal_document"],
            benchmark_info=data["external_benchmark"],
            clauses=data["clauses"],
            metrics=metrics,
        )
        
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
