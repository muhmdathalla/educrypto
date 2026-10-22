# EduCrypto Studio — Professional Monochrome Cryptographic Workbench 🛡️

Aplikasi Web Kriptografi Edukatif & Profesional berstandar industri dengan estetika **Editorial Monochrome (Hitam-Putih Murni)**, animasi background partikel halus, tata letak arsitektur Swiss, **Top Telemetry Header** dengan indikator status modul & **Live Kurs USD / IDR**, serta **Floating Liquid Glass Dock** ala macOS & iOS.

Repository GitHub: [https://github.com/muhmdathalla/educrypto.git](https://github.com/muhmdathalla/educrypto.git)

---

## 🌟 Fitur Utama & Kepatuhan Aturan Kriptografi

Aplikasi ini mempertahankan **100% logika inti kriptografi** asli tanpa mengubah aturan matematis:

1. **Caesar Cipher (Klasik - Substitusi Monoalfabetik)**
   - Pergeseran alfabet Latin di dalam ring $\mathbb{Z}_{26}$.
   - Mempertahankan spasi, angka, dan tanda baca.
   - Dilengkapi pita visualisasi pemetaan alfabet $A \to Z$.

2. **Vigenère Cipher (Klasik - Substitusi Polialfabetik)**
   - Substitusi dinamis berbasis pengulangan kata kunci (*keystream*).
   - Karakter non-alfabet tidak diubah dan tidak mengonsumsi indeks kata kunci (sinkronisasi kunci presisi).
   - Dilengkapi tabel alignment *character-by-character*.

3. **RC4 Cipher (Modern - Stream Cipher Simetris)**
   - Implementasi lengkap KSA (*Key-Scheduling Algorithm*) untuk pengacakan state array S-Box 256-byte.
   - Pembangkitan aliran acak semu PRGA (*Pseudo-Random Generation Algorithm*) dengan operasi bitwise $\text{XOR } (\oplus)$.
   - Inspeksi tabel transformasi byte-by-byte (Plain, Key, Cipher dalam heksadesimal & biner).

4. **RSA PKCS#1 OAEP (Modern - Kriptografi Asimetris)**
   - Pembangkitan pasangan Kunci Publik $(e, n)$ dan Kunci Privat $(d, n)$ (1024 / 2048-bit).
   - Padding standar industri `PKCS#1 OAEP` yang bersifat probabilistik dan tahan terhadap serangan *padding oracle*.
   - Otomatisasi chunking blok OAEP untuk data berukuran panjang.

5. **Super Enkripsi (4-Layer Defense-in-Depth Pipeline)**
   - Alur berantai komposit:
     $$\text{Plaintext} \xrightarrow{\text{Caesar}} \xrightarrow{\text{Vigenère}} \xrightarrow{\text{RC4 Stream}} \xrightarrow{\text{RSA-OAEP}} \text{Ciphertext Akhir (Base64)}$$
   - Pembalikan dekripsi sempurna:
     $$\text{Ciphertext} \xrightarrow{\text{RSA Decrypt}} \xrightarrow{\text{RC4 Decrypt}} \xrightarrow{\text{Vigenère Decrypt}} \xrightarrow{\text{Caesar Decrypt}} \text{Plaintext Asli}$$
   - Visualisasi lonjakan entropi di setiap fase transformasi.

6. **Multimedia & File Vault (Gambar, Audio, Video, PDF, Biner)**
   - Mampu mengenkripsi dan mendekripsi file biner apa pun (PNG, JPG, WAV, MP3, PDF, DOCX, ZIP).
   - Menerapkan arsitektur **Hybrid Digital Envelope** untuk file berukuran besar pada mode RSA/Super.
   - Membungkus output dalam kontainer `.ecry` yang menyimpan metadata dan **Checksum SHA-256** untuk memverifikasi integritas file asli secara otomatis saat didekripsi.
   - Dilengkapi generator sampel instan (Gambar Seal PNG, Audio Sinus Harmonik WAV, dan Dokumen Teks TXT) untuk demonstrasi instan saat sidang.

7. **Security Audit & Cryptanalysis Lab (Fitur Nilai Tambah Sidang Dosen)**
   - **Shannon Entropy $H(X)$:** Menilai tingkat keacakan distribusi informasi (0 hingga 8 bits/byte).
   - **Avalanche Effect:** Pengukuran sensitivitas mutasi 1-bit plaintext terhadap perubahan bit ciphertext.
   - **Index of Coincidence (IoC):** Bukti statistik kerentanan sandi klasik terhadap analisis frekuensi.
   - **Simulasi Serangan Brute-Force Caesar:** Membongkar seluruh 25 kunci kemungkinan secara otomatis dengan pembobotan heuristik bahasa alami.

---

## 🎨 Desain & Tampilan (Senior Web Developer Standard)

- **Pure Editorial Monochrome:** Palet warna monokrom elegan (Obsidian Black `#060606` dan Alabaster White `#F8F8F6`).
- **Bukan Kotak-Kotak AI:** Menggunakan grid arsitektur terbuka (*hairline dividers* $1\text{px}$ tipis) dengan tipografi *Instrument Serif* dipadukan dengan *Plus Jakarta Sans* dan *JetBrains Mono*.
- **Subtle Animated Lattice Background:** Animasi jaring partikel kriptografi dinamis yang bergerak tipis di latar belakang.
- **Top Telemetry Header:**
  - Status aktif mesin kriptografi yang sedang berjalan secara dinamis.
  - Ticker real-time kurs **USD / IDR** dengan sparkline dan popover kalkulator konversi mata uang terpadu.
  - Tombol instan **Sidang / Dosen** untuk membuka rangkuman teori dan jawaban pertanyaan penguji.
  - Switcher tema fleksibel: Mode Gelap (Dark) $\leftrightarrow$ Mode Terang (Light).
- **macOS & iOS Liquid Glass Floating Dock:** Navigasi melayang di bawah layar dengan efek kaca buram (*glassmorphism* $32\text{px}$ blur, saturasi $210\%$, dan *specular hairline border*).

---

## 🚀 Panduan Menjalankan Aplikasi

### Cara 1: Menjalankan Full Web App (Direkomendasikan untuk Presentasi)
Aplikasi web murni dengan server REST API berkecepatan tinggi:
```bash
python3 server.py 8500
```
Buka peramban di: **`http://localhost:8500`**

### Cara 2: Menjalankan via Streamlit
```bash
python3 -m streamlit run app.py
```
Buka peramban di: **`http://localhost:8501`**

---

## 📂 Struktur Berkas
- `server.py`: Server HTTP & REST API multi-threaded untuk melayani seluruh modul kriptografi, kurs USD/IDR, dan audit keamanan.
- `ciphers.py`: Modul logika komputasi kriptografi inti (Caesar, Vigenère, RC4, RSA, Super, File Vault, Entropi Shannon, Avalanche, IoC, Cryptanalysis).
- `web/`:
  - `index.html`: Antarmuka web arsitektur editorial monokrom.
  - `styles.css`: Desain monokrom hitam-putih, non-boxy, hairline grid, dan dock liquid glass macOS/iOS.
  - `app.js`: Pengontrol logika frontend, canvas partikel bergerak, real-time sync, dan generator file sampel.
- `app.py`: Antarmuka alternatif Streamlit dengan tema monokrom dan integrasi 7 modul.
- `requirements.txt`: Dependensi Python (`pycryptodome`, `streamlit`, `pandas`).
- `DOKUMENTASI_PERBAIKAN.md`: Laporan audit komprehensif dan perbaikan bug sistem kriptografi.
