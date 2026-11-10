"""
semantic_retriever.py
Modul Semantic Retrieval (Candidate Selection) berbasis TF-IDF bi-gram dan cosine similarity
untuk memetakan klausul internal bank terhadap pasal regulasi pemerintah yang paling relevan.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Stopwords hukum bahasa Indonesia untuk menepis kata frekuensi tinggi non-spesifik
INDONESIAN_LEGAL_STOPWORDS = [
    "dan", "atau", "yang", "untuk", "dalam", "hal", "pada", "dari", "ke", "oleh",
    "dengan", "sebagaimana", "dimaksud", "ayat", "pasal", "huruf", "angka", "tersebut",
    "adalah", "sebagai", "dapat", "paling", "lama", "hari", "jam", "waktu", "selama",
    "setiap", "kepada", "antara", "secara", "serta", "atas", "bagi", "sampai", "sejak",
]

# Korpus regulasi acuan perbankan nasional
DEFAULT_REGULATORY_CORPUS: List[Dict[str, str]] = [
    {
        "id": "REG-01",
        "regulasi_terkait": "POJK No. 11/POJK.03/2022",
        "pasal_regulasi": "Pasal 27 Ayat (1) dan Ayat (2)",
        "topik": "Pengamanan Kriptografi dan Enkripsi Data Sensitif Nasabah",
        "teks_regulasi": "Bank Umum wajib melakukan pengamanan data dan informasi rahasia nasabah melalui penerapan teknik kriptografi yang andal meliputi enkripsi data pada media penyimpanan dan transmisi data melalui jaringan publik dengan standar keamanan industri terkini.",
    },
    {
        "id": "REG-02",
        "regulasi_terkait": "UU No. 27 Tahun 2022 (UU PDP)",
        "pasal_regulasi": "Pasal 46 Ayat (2)",
        "topik": "Batas Waktu Pemberitahuan Insiden Kegagalan Perlindungan Kebocoran Data Pribadi Nasabah",
        "teks_regulasi": "Dalam hal terjadi insiden kegagalan pelindungan data pribadi atau kebocoran data, Pengendali Data Pribadi wajib menyampaikan pemberitahuan tertulis paling lambat 3 x 24 jam kepada Lembaga dan Subjek Data Pribadi.",
    },
    {
        "id": "REG-03",
        "regulasi_terkait": "POJK No. 11/POJK.03/2022",
        "pasal_regulasi": "Pasal 39 Ayat (3)",
        "topik": "Kelangsungan Operasional BCP dan Recovery Time Objective RTO Pemulihan Bencana DRC",
        "teks_regulasi": "Bank wajib menetapkan Recovery Time Objective RTO untuk sistem pemrosesan transaksi pembayaran paling lama 4 jam sejak insiden terjadi dan memastikan ketersediaan cadangan data pada pusat pemulihan bencana DRC.",
    },
    {
        "id": "REG-04",
        "regulasi_terkait": "POJK No. 11/POJK.03/2022",
        "pasal_regulasi": "Pasal 21 Ayat (1) dan Ayat (3)",
        "topik": "Lokasi Penempatan Pusat Data Center Komputasi Awan Cloud dan Persetujuan Regulator",
        "teks_regulasi": "Bank wajib menempatkan Pusat Data dan Pusat Pemulihan Bencana di wilayah Indonesia. Penempatan data di luar negeri atau cloud hanya dapat dilakukan setelah memperoleh persetujuan Otoritas Jasa Keuangan.",
    },
    {
        "id": "REG-05",
        "regulasi_terkait": "POJK No. 11/POJK.03/2022",
        "pasal_regulasi": "Pasal 29 Ayat (2)",
        "topik": "Pemantauan Keamanan Siber Security Operations Center SOC Berkesinambungan 24 Jam",
        "teks_regulasi": "Bank wajib memiliki unit atau fungsi Security Operations Center yang memantau keamanan sistem informasi dan siber secara berkesinambungan selama 24 jam sehari dan 7 hari seminggu.",
    },
    {
        "id": "REG-06",
        "regulasi_terkait": "PADG Bank Indonesia No. 24/7/PADG/2022",
        "pasal_regulasi": "Pasal 18 Ayat (1)",
        "topik": "Kerahasiaan Data Transaksi Pembayaran dan Perjanjian Kerahasiaan NDA Pihak Ketiga Mitra",
        "teks_regulasi": "Penyelenggara Jasa Pembayaran wajib menjaga kerahasiaan data transaksi serta menjamin kepatuhan pihak ketiga atau mitra penyedia jasa melalui perjanjian kerahasiaan non-disclosure agreement dalam penyelenggaraan sistem pembayaran.",
    },
    {
        "id": "REG-07",
        "regulasi_terkait": "POJK No. 11/POJK.03/2022",
        "pasal_regulasi": "Pasal 15 Ayat (1)",
        "topik": "Manajemen Risiko Pengadaan Penyedia Jasa Teknologi Informasi Vendor IT",
        "teks_regulasi": "Bank wajib melakukan penilaian kelayakan dan uji tuntas due diligence terhadap penyedia jasa teknologi informasi vendor IT sebelum melakukan perikatan kerja sama.",
    },
]


class SemanticRetriever:
    """
    Mesin pencarian semantik untuk mencocokkan klausul SOP internal
    dengan pasal regulasi acuan yang paling relevan.
    """

    def __init__(self, corpus: Optional[List[Dict[str, str]]] = None):
        self.corpus = corpus if corpus is not None else DEFAULT_REGULATORY_CORPUS
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=INDONESIAN_LEGAL_STOPWORDS,
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b",
        )
        self._fit_corpus()

    def _fit_corpus(self):
        # Berikan bobot ganda pada topik agar kluster hukum lebih dominan
        documents = [f"{item['topik']} {item['topik']} {item['teks_regulasi']}" for item in self.corpus]
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def retrieve_best_match(self, internal_clause_text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Mencari pasal regulasi rujukan yang memiliki kemiripan semantik tertinggi.
        """
        query_clean = internal_clause_text.strip()
        if not query_clean:
            return []

        query_vec = self.vectorizer.transform([query_clean])
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            matched_item = dict(self.corpus[idx])
            matched_item["similarity_score"] = round(score, 3)
            results.append(matched_item)

        return results


# Global singleton instance untuk penggunaan cepat di aplikasi
_global_retriever: Optional[SemanticRetriever] = None


def get_default_retriever() -> SemanticRetriever:
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = SemanticRetriever()
    return _global_retriever
