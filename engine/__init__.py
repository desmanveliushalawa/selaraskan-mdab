"""
Package engine untuk keselarasan regulasi perbankan.
"""
from .diff_highlighter import compute_word_diff, render_side_by_side_diff_html
from .alignment_engine import (
    load_benchmark_data,
    calculate_compliance_metrics,
    evaluate_custom_clause_alignment,
)

__all__ = [
    "compute_word_diff",
    "render_side_by_side_diff_html",
    "load_benchmark_data",
    "calculate_compliance_metrics",
    "evaluate_custom_clause_alignment",
]
