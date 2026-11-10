"""
diff_highlighter.py
Modul untuk menghitung perbedaan teks kata-per-kata (word-level diff)
antara klausul internal bank vs regulasi pemerintah, dan merender tampilan
HTML bersanding (side-by-side) dengan sorotan warna merah/hijau ala Big Legal.
"""

import difflib
import re
from typing import Tuple


def tokenize_words(text: str) -> list[str]:
    """Memecah teks menjadi token kata dan spasi/tanda baca secara presisi."""
    return re.findall(r"\w+|[^\w\s]|\s+", text)


def compute_word_diff(text_a: str, text_b: str) -> Tuple[str, str]:
    """
    Menghitung perbedaan tingkat kata antara teks internal (text_a)
    dan teks regulasi rujukan (text_b).
    
    Returns:
        Tuple[str, str]: (html_internal, html_regulasi) dengan tag span styling.
    """
    tokens_a = tokenize_words(text_a)
    tokens_b = tokenize_words(text_b)
    
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    
    html_a_parts = []
    html_b_parts = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        sub_a = "".join(tokens_a[i1:i2])
        sub_b = "".join(tokens_b[j1:j2])
        
        # Escape HTML entities sederhana
        sub_a_escaped = sub_a.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        sub_b_escaped = sub_b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        if tag == "equal":
            html_a_parts.append(sub_a_escaped)
            html_b_parts.append(sub_b_escaped)
        elif tag == "replace":
            # Perbedaan kata (sorot merah pada kalimat internal, sorot kuning/oranye pada regulasi)
            html_a_parts.append(
                f'<span style="background-color: #ffebee; color: #c62828; font-weight: 600; '
                f'padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #ef5350;">'
                f'{sub_a_escaped}</span>'
            )
            html_b_parts.append(
                f'<span style="background-color: #e8f5e9; color: #2e7d32; font-weight: 600; '
                f'padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #66bb6a;">'
                f'{sub_b_escaped}</span>'
            )
        elif tag == "delete":
            # Kata yang ada di internal tapi tidak ada di regulasi
            html_a_parts.append(
                f'<span style="background-color: #ffcdd2; color: #b71c1c; text-decoration: line-through; '
                f'padding: 2px 4px; border-radius: 4px;">{sub_a_escaped}</span>'
            )
        elif tag == "insert":
            # Kata yang ada di regulasi tapi terlewat di internal
            html_b_parts.append(
                f'<span style="background-color: #c8e6c9; color: #1b5e20; font-weight: 600; '
                f'padding: 2px 4px; border-radius: 4px;">{sub_b_escaped}</span>'
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
    Menghasilkan blok HTML perbandingan side-by-side yang meniru tampilan modal Big Legal.
    """
    diff_a, diff_b = compute_word_diff(text_internal, text_regulasi)
    
    status_color = "#c62828" if status == "Tidak Selaras" else ("#2e7d32" if status == "Selaras" else "#f57f17")
    status_bg = "#ffebee" if status == "Tidak Selaras" else ("#e8f5e9" if status == "Selaras" else "#fffde7")
    
    html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e0e0e0;">
            <div>
                <span style="font-size: 13px; color: #666; font-weight: 600; text-transform: uppercase;">Status Evaluasi:</span>
                <span style="background: {status_bg}; color: {status_color}; font-weight: 700; font-size: 13px; padding: 4px 10px; border-radius: 20px; margin-left: 6px; border: 1px solid {status_color};">
                    {status}
                </span>
            </div>
            <div style="font-size: 12px; color: #888;">
                <span style="background: #ffebee; color: #c62828; padding: 2px 6px; border-radius: 3px; font-weight: 600;">Merah: Deviasi Internal</span>
                <span style="background: #e8f5e9; color: #2e7d32; padding: 2px 6px; border-radius: 3px; font-weight: 600; margin-left: 6px;">Hijau: Ketentuan Acuan</span>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 10px;">
            <!-- Kolom Kiri: Internal Bank -->
            <div style="background: #ffffff; border: 1px solid #dcdcdc; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #003d79; font-size: 13px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 2px solid #003d79;">
                    🏛️ KALIMAT INTERNAL BANK (SOP/PO)
                </div>
                <div style="font-size: 11px; color: #666; margin-bottom: 10px; font-style: italic;">
                    {title_internal}
                </div>
                <div style="font-size: 13px; line-height: 1.6; color: #2c3e50; text-align: justify;">
                    {diff_a}
                </div>
            </div>

            <!-- Kolom Kanan: Regulasi Pemerintah -->
            <div style="background: #ffffff; border: 1px solid #dcdcdc; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #1e3c72; font-size: 13px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 2px solid #1e3c72;">
                    ⚖️ KALIMAT REGULASI PEMERINTAH (POJK/UU)
                </div>
                <div style="font-size: 11px; color: #666; margin-bottom: 10px; font-style: italic;">
                    {title_regulasi}
                </div>
                <div style="font-size: 13px; line-height: 1.6; color: #2c3e50; text-align: justify;">
                    {diff_b}
                </div>
            </div>
        </div>
        
        {f'''
        <div style="margin-top: 14px; background: #f8f9fa; border-left: 4px solid #003d79; padding: 10px 14px; border-radius: 0 6px 6px 0;">
            <div style="font-size: 12px; font-weight: 700; color: #003d79; margin-bottom: 4px;">📌 Catatan Analisis Hukum:</div>
            <div style="font-size: 12px; color: #444; line-height: 1.5;">{reasoning}</div>
        </div>
        ''' if reasoning else ''}
    </div>
    """
    return html
