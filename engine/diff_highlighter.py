"""
diff_highlighter.py
Modul komparasi redaksional kata-per-kata (word-level sequence diff)
antara klausul operasional internal bank dan pasal regulasi pemerintah.
Menghasilkan tampilan perbandingan bersanding dengan sorotan deviasi redaksional.
"""

import difflib
import re
import textwrap
from typing import Tuple


def tokenize_words(text: str) -> list[str]:
    """Memecah teks menjadi token kata dan tanda baca secara presisi."""
    return re.findall(r"\w+|[^\w\s]|\s+", text)


def compute_word_diff(text_a: str, text_b: str) -> Tuple[str, str]:
    """
    Menghitung perbedaan tingkat kata antara teks internal (text_a)
    dan teks regulasi rujukan (text_b).
    """
    tokens_a = tokenize_words(text_a)
    tokens_b = tokenize_words(text_b)

    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)

    html_a_parts = []
    html_b_parts = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        sub_a = "".join(tokens_a[i1:i2])
        sub_b = "".join(tokens_b[j1:j2])

        sub_a_escaped = sub_a.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        sub_b_escaped = sub_b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if tag == "equal":
            html_a_parts.append(sub_a_escaped)
            html_b_parts.append(sub_b_escaped)
        elif tag == "replace":
            # Kata yang berbeda disorot dengan kontras tinggi sesuai standar WCAG AA
            html_a_parts.append(
                f'<span style="background-color: #fee2e2; color: #991b1b; font-weight: 600; '
                f'padding: 1px 3px; border-bottom: 2px solid #dc2626;">{sub_a_escaped}</span>'
            )
            html_b_parts.append(
                f'<span style="background-color: #dcfce7; color: #166534; font-weight: 600; '
                f'padding: 1px 3px; border-bottom: 2px solid #16a34a;">{sub_b_escaped}</span>'
            )
        elif tag == "delete":
            html_a_parts.append(
                f'<span style="background-color: #fee2e2; color: #991b1b; text-decoration: line-through; '
                f'padding: 1px 3px;">{sub_a_escaped}</span>'
            )
        elif tag == "insert":
            html_b_parts.append(
                f'<span style="background-color: #dcfce7; color: #166534; font-weight: 600; '
                f'padding: 1px 3px;">{sub_b_escaped}</span>'
            )

    return "".join(html_a_parts), "".join(html_b_parts)


def render_side_by_side_diff_html(
    title_internal: str,
    text_internal: str,
    title_regulasi: str,
    text_regulasi: str,
    status: str = "Tidak Selaras",
    reasoning: str = ""
) -> str:
    """
    Menghasilkan tampilan perbandingan kalimat bersanding yang bersih,
    mengikuti struktur dokumen legal institusional (rujukan Big Legal Telkom).
    Bebas dari ornamen berlebihan dan emoji dekoratif.
    """
    diff_a, diff_b = compute_word_diff(text_internal, text_regulasi)

    status_styles = {
        "Tidak Selaras": ("#991b1b", "#fef2f2", "#fecaca"),
        "Selaras": ("#166534", "#f0fdf4", "#bbf7d0"),
        "Netral": ("#854d0e", "#fefce8", "#fef08a"),
    }
    color, bg, border = status_styles.get(status, ("#334155", "#f1f5f9", "#cbd5e1"))

    reasoning_section = ""
    if reasoning:
        reasoning_section = (
            f'<div style="margin-top: 14px; padding: 12px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px;">'
            f'<div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Pertimbangan Hukum:</div>'
            f'<div style="font-size: 13px; color: #1e293b; line-height: 1.5;">{reasoning}</div>'
            f'</div>'
        )

    html = (
        f'<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif; color: #0f172a; margin-bottom: 12px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; margin-bottom: 14px;">'
        f'<div style="display: flex; align-items: center; gap: 8px;">'
        f'<span style="font-size: 12px; color: #64748b; font-weight: 600;">STATUS HASIL UJI:</span>'
        f'<span style="background: {bg}; color: {color}; border: 1px solid {border}; font-weight: 700; font-size: 12px; padding: 2px 8px; border-radius: 4px;">{status.upper()}</span>'
        f'</div>'
        f'<div style="font-size: 11px; color: #64748b;">'
        f'<span style="background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 2px; font-weight: 600;">Merah: Deviasi Internal</span>'
        f'<span style="background: #dcfce7; color: #166534; padding: 2px 6px; border-radius: 2px; font-weight: 600; margin-left: 6px;">Hijau: Ketentuan Acuan</span>'
        f'</div>'
        f'</div>'
        f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">'
        f'<div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 12px;">'
        f'<div style="font-size: 11px; font-weight: 700; color: #003d79; text-transform: uppercase; margin-bottom: 4px;">Kalimat Dokumen Internal Bank</div>'
        f'<div style="font-size: 11px; color: #64748b; margin-bottom: 8px; font-weight: 500;">{title_internal}</div>'
        f'<div style="font-size: 13px; line-height: 1.6; color: #1e293b; text-align: justify;">{diff_a}</div>'
        f'</div>'
        f'<div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 12px;">'
        f'<div style="font-size: 11px; font-weight: 700; color: #003d79; text-transform: uppercase; margin-bottom: 4px;">Kalimat Peraturan Pemerintah / Regulator</div>'
        f'<div style="font-size: 11px; color: #64748b; margin-bottom: 8px; font-weight: 500;">{title_regulasi}</div>'
        f'<div style="font-size: 13px; line-height: 1.6; color: #1e293b; text-align: justify;">{diff_b}</div>'
        f'</div>'
        f'</div>'
        f'{reasoning_section}'
        f'</div>'
    )
    return html
