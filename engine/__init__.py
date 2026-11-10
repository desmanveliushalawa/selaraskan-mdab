"""
Package engine untuk keselarasan regulasi perbankan.
"""
from .diff_highlighter import compute_word_diff, render_side_by_side_diff_html
from .alignment_engine import (
    load_benchmark_data,
    calculate_compliance_metrics,
    evaluate_custom_clause_alignment,
)
from .legal_parser import extract_raw_text, parse_legal_structure

__all__ = [
    "compute_word_diff",
    "render_side_by_side_diff_html",
    "load_benchmark_data",
    "calculate_compliance_metrics",
    "evaluate_custom_clause_alignment",
    "extract_raw_text",
    "parse_legal_structure",
]
