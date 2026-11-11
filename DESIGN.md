# DESIGN.md : SELARASKAN MDAB Design System

Sistem Desain Institusional Perbankan & Legal-Tech Kepatuhan Regulasi Bank Mandiri.

## 1. Identitas & Karakter Desain
- **Karakter:** Formal, presisi, institusional, otoritatif, dan berbasis bukti hukum (*evidence-based*).
- **Domain:** Audit Kepatuhan Regulasi Perbankan (POJK, Bank Indonesia, UU PDP, Kebijakan Internal Mandiri).
- **Prinsip Desain:** Bebas dari ornamen AI generik (tanpa animasi melayang, tanpa gradient ungu-biru, tanpa sudut membulat pil ekstrim, tanpa bayangan tebal).

## 2. Parameter Dials (Standar Kerapian Desain)
- **ENERGY: 1 (Calm)** : Antarmuka tenang, fokus membaca teks hukum panjang, minim distraksi visual.
- **RHYTHM: 1 (Uniform)** : Tata letak grid dan kartu terstruktur seragam sesuai standar master data perbankan.
- **MOTION: 1 (Static)** : Transisi visual statis, pergerakan hanya terjadi pada status loading dan interaksi langsung pengguna.

## 3. Palet Warna (Color Palette Standards : R-29 & R-25)
- **Brand Primary:** `#003d79` (Bank Mandiri Deep Navy) : Digunakan pada judul utama, header, dan batas fokus.
- **Latar Belakang:** `#ffffff` (Card background) dan `#f8fafc` (Slate-50 neutral panel).
- **Tipografi Utama:**
  - Teks Judul / Utama: `#0f172a` (Slate-900)
  - Teks Konten / Paragraf: `#1e293b` (Slate-800) dan `#334155` (Slate-700)
  - Teks Sekunder / Meta / Label: `#475569` (Slate-600) : Kontras rasio 7.24:1 terhadap `#f8fafc` (Lolos WCAG AAA).
- **Status Semantik Kepatuhan (Compliance Matrix):**
  - **Selaras:** Teks `#166534`, Latar `#f0fdf4`, Border `#bbf7d0`
  - **Tidak Selaras:** Teks `#991b1b`, Latar `#fef2f2`, Border `#fecaca`
  - **Netral:** Teks `#854d0e`, Latar `#fefce8`, Border `#fef08a`

## 4. Tipografi & Border Radius
- **Font Family:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Border Radius:** `4px` konsisten pada seluruh komponen (kartu, tombol, input, badge). Memberikan kesan struktural dan tegas, menghindari gaya mainan / aplikasi konsumen.
- **Aksen Garis:** Border solid `1px` berwarna `#cbd5e1` (Slate-300) atau `#e2e8f0` (Slate-200). Tanpa bayangan mengambang (`box-shadow: none`).
