"""
Package engine untuk keselarasan regulasi perbankan.
"""
from .diff_highlighter import compute_word_diff, render_side_by_side_diff_html
from .alignment_engine import (
    load_benchmark_data,
    calculate_compliance_metrics,
    evaluate_custom_clause_alignment,
    link_rapat_teknis_to_clauses,
)
from .legal_parser import extract_raw_text, parse_legal_structure
from .report_generator import generate_compliance_pdf_report
from .semantic_retriever import SemanticRetriever, get_default_retriever
from .rapat_teknis_manager import (
    list_rapat_teknis,
    get_rapat_teknis,
    save_rapat_teknis,
    delete_rapat_teknis,
    find_rapat_teknis_for_target,
)
from .rapat_teknis_parser import (
    parse_rapat_teknis_file,
    parse_rapat_teknis_docx,
    parse_rapat_teknis_csv,
)

__all__ = [
    "compute_word_diff",
    "render_side_by_side_diff_html",
    "load_benchmark_data",
    "calculate_compliance_metrics",
    "evaluate_custom_clause_alignment",
    "link_rapat_teknis_to_clauses",
    "extract_raw_text",
    "parse_legal_structure",
    "generate_compliance_pdf_report",
    "SemanticRetriever",
    "get_default_retriever",
    "list_rapat_teknis",
    "get_rapat_teknis",
    "save_rapat_teknis",
    "delete_rapat_teknis",
    "find_rapat_teknis_for_target",
    "parse_rapat_teknis_file",
    "parse_rapat_teknis_docx",
    "parse_rapat_teknis_csv",
]
