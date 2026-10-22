# 📑 Dokumentasi Komprehensif Analisis, Debugging, dan Perbaikan Sistem Kriptografi

**Nama Aplikasi:** EduCrypto Studio (Laboratorium Kriptografi Interaktif)  
**Lingkungan:** Python 3.14 / Streamlit / PyCryptodome  
**File Terdampak:**
- [`ciphers.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/ciphers.py) (Modul Inti Kriptografi)
- [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py) (Antarmuka Pengguna Streamlit)

---

## 🎯 Ringkasan Eksekutif

Dokumentasi ini merangkum seluruh temuan kesalahan, perbaikan logika enkripsi/dekripsi, serta optimasi antarmuka (UI/UX) pada aplikasi **EduCrypto Studio**, yang mencakup 5 modul:
1. **Caesar Cipher** (Klasik - Substitusi Monoalfabetik)
2. **Vigenère Cipher** (Klasik - Substitusi Polialfabetik)
3. **RC4 Stream Cipher** (Modern Simetris)
4. **RSA Asymmetric Cipher** (Modern Asimetris PKCS#1 OAEP)
5. **Super Enkripsi & Dekripsi** (Pipeline 4-Lapis Berantai)

Perbaikan dibagi menjadi dua sesi terstruktur:
* **Sesi Perbaikan 1:** Fokus pada perbaikan bug kritis RSA (state synchronization Streamlit, TypeError, edge case padding).
* **Sesi Perbaikan 2:** Audit menyeluruh metode 1 sampai 5 (perbaikan typo teks contoh bawaan, auto-sinkronisasi parameter enkripsi ke dekripsi, dan inisialisasi default kunci).

---

## 🔹 Sesi Perbaikan 1: Penanganan Bug Kritis RSA & Sinkronisasi Widget UI

Pada sesi awal, dilakukan audit mendalam pada modul RSA di [`ciphers.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/ciphers.py) dan [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py).

### 1. Masalah Kunci Tidak Ter-update di Layar (Streamlit Widget Key Isolation)
* **Gejala:** Saat pengguna menekan *"Generate Kunci Baru"* (baik 1024-bit maupun 2048-bit), kotak tampilan Public Key dan Private Key tidak berubah di layar browser.
* **Penyebab:** Di Streamlit, widget dengan parameter `key` (seperti `key="area_pub_key"`) hanya membaca parameter `value=` saat inisialisasi pertama. Pada proses *rerun*, Streamlit mengabaikan `value=` dan hanya membaca isi `st.session_state["area_pub_key"]`.
* **Solusi Kode:** Pada tombol generator, nilai kunci langsung disuntikkan ke key widget yang bersangkutan:
  ```python
  pub, priv = generate_rsa_keys(key_size)
  st.session_state["rsa_pub"] = pub
  st.session_state["rsa_priv"] = priv
  st.session_state["area_pub_key"] = pub
  st.session_state["area_priv_key"] = priv
  st.session_state["rsa_pub_use"] = pub
  st.session_state["rsa_priv_use"] = priv
  st.rerun()
  ```

### 2. Error Mentah `TypeError: This is not a private key`
* **Gejala:** Jika pengguna salah memasukkan Public Key ke form Private Key saat dekripsi, sistem melempar `TypeError` yang belum tertangani.
* **Solusi Kode (`ciphers.py`):**
  ```python
  if not rsa_key.has_private():
      raise ValueError("Kunci yang dimasukkan adalah Public Key. Dekripsi RSA memerlukan Private Key.")
  ```

### 3. Edge Case Data Kosong pada `rsa_encrypt`
* **Gejala:** Enkripsi byte kosong `b""` menghasilkan byte kosong `b""` (0 byte), padahal standar RSA PKCS#1 OAEP seharusnya mengenkripsi padding OAEP menjadi 1 blok ciphertext utuh.
* **Solusi Kode (`ciphers.py`):**
  ```python
  if len(data) == 0:
      return cipher.encrypt(b"")
  ```

### 4. Fleksibilitas Panjang Kunci pada Super Enkripsi
* **Gejala:** Tombol generate kunci RSA di menu Super Enkripsi di-hardcode ke 2048-bit saja tanpa opsi 1024-bit.
* **Solusi Kode (`app.py`):** Ditambahkan dropdown pilihan ukuran bit (1024 / 2048-bit) di form Super Enkripsi.

---

## 🔹 Sesi Perbaikan 2: Audit Menyeluruh Metode 1 s/d 5 (Logic, Default Data & Auto-Sync)

Pada sesi kedua, dilakukan pengujian end-to-end pada kelima modul untuk memastikan alur enkripsi hingga dekripsi berjalan mulus tanpa hambatan manual.

### 1. Metode 1: Caesar Cipher
* **Temuan:**
  * Typo pada contoh ciphertext bawaan di tab Dekripsi: `"phqmjdnhudkdvlddq"` (kurang spasi dan salah huruf 'j'). Saat didekripsi dengan shift 3, menghasilkan `"Kriptografi adalah seni menjgakerahasiaan informasi."` (kata "menjaga" dan "kerahasiaan" menyatu).
  * Pengguna harus menyalin manual hasil enkripsi jika ingin mengujinya di tab Dekripsi.
* **Perbaikan di [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py):**
  * Memperbaiki teks contoh default ciphertext menjadi: `"Nulswrjudil dgdodk vhql phqmdjd nhudkdvlddq lqirupdvl."`.
  * Menambahkan **auto-sinkronisasi**: setelah tombol *"Enkripsi Sekarang"* ditekan, ciphertext dan nilai shift langsung diteruskan ke tab Dekripsi (`st.session_state["caesar_dec_input"]` dan `st.session_state["caesar_shift_dec"]`).

### 2. Metode 2: Vigenère Cipher
* **Temuan:**
  * Contoh default ciphertext di tab Dekripsi berisi teks placeholder palsu: `"Yevgng suyah ji bukit timur..."`. Saat didekripsi dengan kunci `"GARUDA"`, menghasilkan karakter acak yang rusak: `"Seemkg muhge jc bdqft nivao..."`.
* **Perbaikan di [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py):**
  * Memperbaiki teks contoh default ciphertext dengan ciphertext resmi yang valid: `"Yeiuqg sujok do blelt zidou sgak zdjgr kcea!"`. Saat didekripsi dengan kunci `"GARUDA"`, teks langsung pulih sempurna menjadi `"Serang musuh di bukit timur saat fajar tiba!"`.
  * Menambahkan **auto-sinkronisasi**: hasil enkripsi dan kata kunci otomatis diisi ke tab Dekripsi (`st.session_state["vig_dec_input"]` dan `st.session_state["vig_key_dec"]`).

### 3. Metode 3: RC4 Stream Cipher
* **Temuan:**
  * Tab Dekripsi menyediakan radio pilihan format: `"Hexadecimal"` (default) dan `"Base64"`. Namun ciphertext hasil enkripsi sebelumnya tidak terhubung ke tab Dekripsi sehingga pengguna harus bolak-balik menyalin string hex/base64.
* **Perbaikan di [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py):**
  * Menambahkan **auto-sinkronisasi**: saat enkripsi RC4 selesai, ciphertext dalam format Hexadecimal (sesuai pilihan radio default dekripsi) dan kunci rahasianya otomatis diisikan ke tab Dekripsi (`st.session_state["rc4_dec_input"]` dan `st.session_state["rc4_key_dec"]`).

### 4. Metode 4: RSA Cipher
* **Temuan:**
  * Saat pertama kali aplikasi dibuka dan pengguna langsung menuju tab RSA, form Public Key dan Private Key kosong sebelum tombol generate ditekan.
  * Hasil ciphertext RSA (Base64) belum otomatis disinkronkan ke tab Dekripsi.
* **Perbaikan di [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py):**
  * Inisialisasi pasangan kunci default 2048-bit pada startup aplikasi, sehingga form RSA langsung terisi dan siap digunakan tanpa harus generate kunci terlebih dahulu.
  * Menambahkan auto-sinkronisasi hasil ciphertext Base64 ke tab Dekripsi (`st.session_state["rsa_cipher_use"]`).

### 5. Metode 5: Super Enkripsi (Multi-Layer Pipeline)
* **Temuan Kritis:**
  * Jika pengguna mengubah parameter di Tab Enkripsi (misal: Caesar Shift diubah ke 12, kunci Vigenère diubah ke "INDONESIA", dan kunci RC4 diganti), lalu menekan *"Mulai Proses Super Enkripsi"*, tab Super Dekripsi **tidak mengikuti kunci-kunci baru tersebut** (masih menggunakan nilai lama 7, NUSANTARA, KunciStreamRC42026).
  * Akibatnya, saat pengguna mengklik tombol dekripsi, proses gagal dengan error: `"Gagal mendekode byte hasil RC4 ke teks UTF-8. Pastikan kunci RC4 benar."`
* **Perbaikan di [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py):**
  * Menyinkronkan seluruh parameter enkripsi ke form dekripsi secara otomatis saat enkripsi dieksekusi:
    ```python
    st.session_state["super_dec_caesar_shift"] = int(s_caesar_shift)
    st.session_state["super_dec_vig_key"] = s_vig_key
    st.session_state["super_dec_rc4_key"] = s_rc4_key
    st.session_state["super_dec_rsa_priv_in"] = st.session_state["rsa_priv"]
    st.session_state["super_dec_cipher_in"] = enc_details["final_ciphertext"]
    ```
  * Hasilnya, proses Super Dekripsi kini 100% konsisten dan instan tanpa risiko kegagalan pencocokan kunci.

---

## 🧪 Tabel Verifikasi & Hasil Pengujian

Seluruh alur enkripsi dan dekripsi telah diuji secara otomatis menggunakan suite pengujian `streamlit.testing.v1.AppTest`:

| No | Modul Algoritma | Skenario Pengujian | Hasil Pengujian | Status |
|:--:|:---|:---|:---|:--:|
| 1 | **Caesar Cipher** | Enkripsi teks lalu dekripsi otomatis | Plaintext asli pulih 100% | **LULUS (Passed)** |
| 2 | **Caesar Cipher** | Dekripsi teks contoh default | Teks "menjaga kerahasiaan" rapi tanpa typo | **LULUS (Passed)** |
| 3 | **Vigenère Cipher** | Enkripsi dengan kata kunci custom | Plaintext asli pulih 100% | **LULUS (Passed)** |
| 4 | **Vigenère Cipher** | Dekripsi teks contoh default | Pulih ke teks asli tanpa placeholder rusak | **LULUS (Passed)** |
| 5 | **RC4 Cipher** | Enkripsi stream -> Auto-sync Hex -> Dekripsi | Plaintext asli pulih 100% | **LULUS (Passed)** |
| 6 | **RSA Cipher** | Generate 1024-bit vs 2048-bit | UI langsung berubah dinamis sesuai bit | **LULUS (Passed)** |
| 7 | **RSA Cipher** | Dekripsi dengan Public Key | Error informatif `ValueError` (Bukan `TypeError`) | **LULUS (Passed)** |
| 8 | **RSA Cipher** | Enkripsi data byte kosong `b""` | Berhasil dengan 1 blok padding OAEP | **LULUS (Passed)** |
| 9 | **Super Enkripsi** | Pipeline 4 lapis -> Sinkronisasi kunci & ciphertext -> Super Dekripsi | Plaintext awal pulih 100% tanpa error kunci | **LULUS (Passed)** |

---

## 💡 Panduan Review bagi Pengguna

Semua perubahan pada kode telah selesai diimplementasikan dengan komentar penjelas yang rapi.
1. Buka tab file [`ciphers.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/ciphers.py) dan [`app.py`](file:///c:/Users/VICTUS/Documents/kuliah/Semester%205/Kriptografi/good_kripto/app.py) di IDE Anda untuk meninjau perbedaan kode (*diff*).
2. Klik tombol **Accept** pada IDE untuk menyetujui perubahan kode.
3. Jalankan aplikasi Streamlit untuk melihat tampilan antarmuka yang kini sudah sinkron dan bebas dari error:
   ```bash
   streamlit run app.py
   ```
