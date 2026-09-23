# EduCrypto Studio 🔐
Aplikasi Edukasi Kriptografi Berbasis Python & Streamlit.

## 📌 Ringkasan Fitur
Aplikasi ini menyediakan laboratorium interaktif untuk mempelajari algoritma kriptografi klasik hingga modern, serta kombinasi multi-layer (**Super Enkripsi**):

1. **Caesar Cipher**: Substitusi monoalfabetik klasik dengan visualisasi tabel pergeseran (*shift* $k$).
2. **Vigenère Cipher**: Substitusi polialfabetik dinamis berbasis kata kunci berulang (*keystream*).
3. **RC4 Cipher**: Stream cipher simetris modern dengan visualisasi algoritma *Key-Scheduling Algorithm* (KSA) dan *Pseudo-Random Generation Algorithm* (PRGA), serta format ciphertext Hexadecimal & Base64.
4. **RSA Cipher**: Kriptografi asimetris modern standar industri (`PKCS#1 OAEP`) dengan generator pasangan Public & Private Key (1024 / 2048-bit) dan dukungan enkripsi *chunking* otomatis untuk teks panjang.
5. **Super Enkripsi**: Pipeline berantai 4 lapis perlindungan mendalam (*Defense in Depth*):
   $$\text{Plaintext} \xrightarrow{\text{Caesar}} \xrightarrow{\text{Vigenère}} \xrightarrow{\text{RC4}} \xrightarrow{\text{RSA}} \text{Ciphertext Akhir (Base64)}$$
   Disertai visualisasi langkah demi langkah (*step-by-step*) perubahan bentuk pesan di setiap fase enkripsi dan dekripsi.

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Masuk ke Direktori Proyek
```bash
cd crypto_app
```

### 2. Pasang Dependensi
Pastikan Python telah terinstal, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi Streamlit
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser lokal Anda di alamat `http://localhost:8501`.

---

## 📂 Struktur File
- `app.py`: Antarmuka grafis (UI) interaktif Streamlit dengan navigasi 5 modul dan visualisasi step-by-step.
- `ciphers.py`: Modul logika komputasi inti seluruh algoritma kriptografi.
- `requirements.txt`: Daftar pustaka Python (`streamlit` dan `pycryptodome`).
