import streamlit as st
import base64
import pandas as pd
from ciphers import (
    encrypt_caesar, decrypt_caesar,
    encrypt_vigenere, decrypt_vigenere,
    rc4_crypt,
    generate_rsa_keys, rsa_encrypt, rsa_decrypt,
    super_encrypt, super_decrypt
)

# ==============================================================================
# KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="EduCrypto - Laboratorium Kriptografi Interaktif",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan elegan dan modern
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .crypto-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #2563EB;
        margin-bottom: 1rem;
    }
    .metric-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #EEF2FF;
        color: #3730A3;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Session State
if "rsa_pub" not in st.session_state:
    st.session_state["rsa_pub"] = ""
if "rsa_priv" not in st.session_state:
    st.session_state["rsa_priv"] = ""
if "super_last_ciphertext" not in st.session_state:
    st.session_state["super_last_ciphertext"] = ""


# ==============================================================================
# SIDEBAR NAVIGASI
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/security-shield.png", width=70)
    st.title("🔐 EduCrypto Studio")
    st.caption("Eksplorasi Kriptografi Klasik hingga Super Enkripsi Modern")
    st.markdown("---")

    menu = st.radio(
        "Pilih Modul Algoritma:",
        [
            "1. Caesar Cipher",
            "2. Vigenère Cipher",
            "3. RC4 Cipher",
            "4. RSA Cipher",
            "5. Super Enkripsi"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### ℹ️ Info Lab")
    st.markdown(
        """
        - **Klasik:** Substitusi Mono/Polialfabetik
        - **Modern:** Stream & Asimetris
        - **Super Enkripsi:** Pipeline Berantai 4 Lapis
        """
    )


# ==============================================================================
# HALAMAN 1: CAESAR CIPHER
# ==============================================================================
if menu == "1. Caesar Cipher":
    st.markdown('<div class="main-title">🏛️ Caesar Cipher</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Algoritma substitusi monoalfabetik klasik dengan pergeseran posisi alfabet standar.</div>', unsafe_allow_html=True)

    with st.expander("📖 Konsep Matematis Caesar Cipher", expanded=False):
        st.markdown(r"""
        Setiap huruf pada teks terang digeser sebanyak $k$ langkah di dalam alfabet:
        - **Enkripsi:** $C = (P + k) \pmod{26}$
        - **Dekripsi:** $P = (C - k) \pmod{26}$
        
        *Karakter non-alfabet (spasi, angka, tanda baca) dipertahankan.*
        """)

    tab_enc, tab_dec, tab_vis = st.tabs(["🔒 Enkripsi", "🔓 Dekripsi", "🔍 Visualisasi Pergeseran"])

    with tab_enc:
        col1, col2 = st.columns([3, 1])
        with col1:
            caesar_input = st.text_area(
                "Teks Terang (Plaintext):",
                value="Kriptografi adalah seni menjaga kerahasiaan informasi.",
                height=120,
                key="caesar_enc_input"
            )
        with col2:
            shift_enc = st.number_input("Nilai Pergeseran (Shift / Kunci):", min_value=1, max_value=25, value=3, step=1, key="caesar_shift_enc")
            st.info(f"Setiap huruf digeser **+{shift_enc}** langkah.")

        if st.button("Enkripsi Sekarang", type="primary", key="btn_caesar_enc"):
            if caesar_input:
                result = encrypt_caesar(caesar_input, shift_enc)
                st.success("Teks berhasil dienkripsi!")
                st.text_area("Hasil Ciphertext:", value=result, height=120, key="caesar_enc_res")
                st.caption(f"Panjang Karakter: {len(result)}")
            else:
                st.warning("Silakan masukkan teks terlebih dahulu.")

    with tab_dec:
        col1, col2 = st.columns([3, 1])
        with col1:
            caesar_dec_input = st.text_area(
                "Teks Sandi (Ciphertext):",
                value="Nulswrjudil dgdodk vhql phqmjdnhudkdvlddq lqirupdvl.",
                height=120,
                key="caesar_dec_input"
            )
        with col2:
            shift_dec = st.number_input("Nilai Pergeseran (Shift / Kunci):", min_value=1, max_value=25, value=3, step=1, key="caesar_shift_dec")
            st.info(f"Setiap huruf dikembalikan **-{shift_dec}** langkah.")

        if st.button("Dekripsi Sekarang", type="primary", key="btn_caesar_dec"):
            if caesar_dec_input:
                result = decrypt_caesar(caesar_dec_input, shift_dec)
                st.success("Teks berhasil didekripsi!")
                st.text_area("Hasil Plaintext:", value=result, height=120, key="caesar_dec_res")
            else:
                st.warning("Silakan masukkan ciphertext terlebih dahulu.")

    with tab_vis:
        st.markdown("#### Tabel Pemetaan Alfabet")
        sample_shift = st.slider("Pilih Shift untuk melihat pemetaan:", min_value=1, max_value=25, value=3)
        orig_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        mapped_letters = [chr((i - ord('A') + sample_shift) % 26 + ord('A')) for i in range(ord('A'), ord('Z') + 1)]
        df_map = pd.DataFrame({"Plain": orig_letters, f"Shift +{sample_shift}": mapped_letters}).T
        st.dataframe(df_map, use_container_width=True)


# ==============================================================================
# HALAMAN 2: VIGENÈRE CIPHER
# ==============================================================================
elif menu == "2. Vigenère Cipher":
    st.markdown('<div class="main-title">🗝️ Vigenère Cipher</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Algoritma substitusi polialfabetik menggunakan kata kunci berulang untuk mengubah nilai pergeseran secara dinamis.</div>', unsafe_allow_html=True)

    with st.expander("📖 Konsep Matematis Vigenère Cipher", expanded=False):
        st.markdown(r"""
        Vigenère menggunakan deretan sandi Caesar berdasarkan huruf-huruf pada kata kunci:
        - **Enkripsi:** $C_i = (P_i + K_{i \pmod m}) \pmod{26}$
        - **Dekripsi:** $P_i = (C_i - K_{i \pmod m}) \pmod{26}$
        
        Karakter non-alfabet tidak diubah dan tidak menggeser posisi indeks kunci.
        """)

    tab_enc, tab_dec = st.tabs(["🔒 Enkripsi", "🔓 Dekripsi"])

    with tab_enc:
        col1, col2 = st.columns([3, 1])
        with col1:
            vig_input = st.text_area(
                "Teks Terang (Plaintext):",
                value="Serang musuh di bukit timur saat fajar tiba!",
                height=120,
                key="vig_enc_input"
            )
        with col2:
            vig_key_enc = st.text_input("Kata Kunci (Key):", value="GARUDA", key="vig_key_enc")
            st.caption("Kunci hanya memperhitungkan huruf alfabet (A-Z).")

        if st.button("Enkripsi Sekarang", type="primary", key="btn_vig_enc"):
            if vig_input and vig_key_enc:
                try:
                    result = encrypt_vigenere(vig_input, vig_key_enc)
                    st.success("Teks berhasil dienkripsi!")
                    st.text_area("Hasil Ciphertext:", value=result, height=120, key="vig_enc_res")
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning("Mohon isi teks dan kata kunci.")

    with tab_dec:
        col1, col2 = st.columns([3, 1])
        with col1:
            vig_dec_input = st.text_area(
                "Teks Sandi (Ciphertext):",
                value="Yevgng suyah ji bukit timur...",
                height=120,
                key="vig_dec_input"
            )
        with col2:
            vig_key_dec = st.text_input("Kata Kunci (Key):", value="GARUDA", key="vig_key_dec")

        if st.button("Dekripsi Sekarang", type="primary", key="btn_vig_dec"):
            if vig_dec_input and vig_key_dec:
                try:
                    result = decrypt_vigenere(vig_dec_input, vig_key_dec)
                    st.success("Teks berhasil didekripsi!")
                    st.text_area("Hasil Plaintext:", value=result, height=120, key="vig_dec_res")
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning("Mohon isi teks sandi dan kata kunci.")


# ==============================================================================
# HALAMAN 3: RC4 CIPHER
# ==============================================================================
elif menu == "3. RC4 Cipher":
    st.markdown('<div class="main-title">⚡ RC4 (Rivest Cipher 4)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Stream cipher simetris modern berbasis permutasi array byte 0–255 (KSA) dan pembangkitan keystream (PRGA).</div>', unsafe_allow_html=True)

    with st.expander("📖 Arsitektur Internal RC4", expanded=False):
        st.markdown(r"""
        RC4 bekerja dalam 2 fase:
        1. **KSA (Key-Scheduling Algorithm):** Menginisialisasi tabel substitusi $S$-box (panjang 256) menggunakan kunci rahasia.
        2. **PRGA (Pseudo-Random Generation Algorithm):** Menghasilkan aliran byte acak (*keystream*) semu secara terus menerus.
        
        Operasi enkripsi dan dekripsi menggunakan operasi **XOR ($\oplus$)**:
        $$C_i = P_i \oplus K_i \quad \text{dan} \quad P_i = C_i \oplus K_i$$
        """)

    tab_enc, tab_dec = st.tabs(["🔒 Enkripsi (Text -> Hex/Base64)", "🔓 Dekripsi (Hex/Base64 -> Text)"])

    with tab_enc:
        col1, col2 = st.columns([3, 1])
        with col1:
            rc4_input = st.text_area("Pesan Teks (Plaintext):", value="Data rahasia transaksi perbankan 2026", height=120, key="rc4_enc_input")
        with col2:
            rc4_key_enc = st.text_input("Kunci Rahasia RC4:", value="SecretKey123!", type="password", key="rc4_key_enc")

        if st.button("Enkripsi RC4", type="primary", key="btn_rc4_enc"):
            if rc4_input and rc4_key_enc:
                try:
                    data_bytes = rc4_input.encode('utf-8')
                    key_bytes = rc4_key_enc.encode('utf-8')
                    cipher_bytes = rc4_crypt(data_bytes, key_bytes)
                    
                    hex_out = cipher_bytes.hex()
                    b64_out = base64.b64encode(cipher_bytes).decode('ascii')

                    st.success("Teks berhasil dienkripsi!")
                    
                    st.markdown("**Hasil Ciphertext (Hexadecimal):**")
                    st.code(hex_out, language="text")

                    st.markdown("**Hasil Ciphertext (Base64):**")
                    st.code(b64_out, language="text")
                    
                    st.caption(f"Ukuran Data: {len(data_bytes)} byte input → {len(cipher_bytes)} byte output.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
            else:
                st.warning("Mohon isi pesan dan kunci.")

    with tab_dec:
        col1, col2 = st.columns([3, 1])
        with col1:
            format_choice = st.radio("Format Ciphertext Input:", ["Hexadecimal", "Base64"], horizontal=True)
            rc4_dec_input = st.text_area("Ciphertext:", height=100, key="rc4_dec_input")
        with col2:
            rc4_key_dec = st.text_input("Kunci Rahasia RC4:", value="SecretKey123!", type="password", key="rc4_key_dec")

        if st.button("Dekripsi RC4", type="primary", key="btn_rc4_dec"):
            if rc4_dec_input and rc4_key_dec:
                try:
                    cleaned_input = "".join(rc4_dec_input.split())
                    if format_choice == "Hexadecimal":
                        cipher_bytes = bytes.fromhex(cleaned_input)
                    else:
                        cipher_bytes = base64.b64decode(cleaned_input)

                    key_bytes = rc4_key_dec.encode('utf-8')
                    recovered_bytes = rc4_crypt(cipher_bytes, key_bytes)
                    recovered_text = recovered_bytes.decode('utf-8')

                    st.success("Ciphertext berhasil didekripsi!")
                    st.text_area("Plaintext Asli:", value=recovered_text, height=120)
                except Exception as e:
                    st.error(f"Gagal mendekripsi: {e}. Pastikan format input dan kunci benar.")
            else:
                st.warning("Mohon isi ciphertext dan kunci.")


# ==============================================================================
# HALAMAN 4: RSA CIPHER
# ==============================================================================
elif menu == "4. RSA Cipher":
    st.markdown('<div class="main-title">🛡️ RSA (Rivest-Shamir-Adleman)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Algoritma kriptografi asimetris dengan pasangan kunci (Kunci Publik untuk enkripsi dan Kunci Privat untuk dekripsi) menggunakan standar PKCS#1 OAEP.</div>', unsafe_allow_html=True)

    with st.expander("📖 Konsep Matematis RSA", expanded=False):
        st.markdown(r"""
        RSA memanfaatkan kesulitan faktorisasi bilangan prima berukuran besar:
        1. Pilih dua bilangan prima besar $p$ dan $q$, hitung modulus $n = p \times q$.
        2. Hitung totient $\phi(n) = (p-1)(q-1)$.
        3. Pilih eksponen publik $e$ sedemikian sehingga $\gcd(e, \phi(n)) = 1$.
        4. Hitung eksponen privat $d$ sehingga $d \times e \equiv 1 \pmod{\phi(n)}$.
        5. **Public Key:** $(e, n)$ | **Private Key:** $(d, n)$
        - Enkripsi: $C \equiv M^e \pmod n$
        - Dekripsi: $M \equiv C^d \pmod n$
        """)

    st.markdown("### 🔑 Pembangkitan Pasangan Kunci RSA (Key Generator)")
    col_gen1, col_gen2 = st.columns([1, 3])
    with col_gen1:
        key_size = st.selectbox("Panjang Kunci (Bits):", [1024, 2048], index=1)
        if st.button("Generate Kunci Baru", type="secondary", use_container_width=True):
            with st.spinner("Menghasilkan bilangan prima dan kunci RSA..."):
                pub, priv = generate_rsa_keys(key_size)
                st.session_state["rsa_pub"] = pub
                st.session_state["rsa_priv"] = priv
                st.success("Kunci berhasil digenerate!")

    with col_gen2:
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.text_area("Public Key (PEM):", value=st.session_state["rsa_pub"], height=140, key="area_pub_key")
        with col_k2:
            st.text_area("Private Key (PEM):", value=st.session_state["rsa_priv"], height=140, key="area_priv_key")

    st.markdown("---")
    tab_enc, tab_dec = st.tabs(["🔒 Enkripsi dengan Public Key", "🔓 Dekripsi dengan Private Key"])

    with tab_enc:
        col1, col2 = st.columns(2)
        with col1:
            rsa_plain = st.text_area("Plaintext:", value="Kerahasiaan data menggunakan RSA 2048-bit", height=120, key="rsa_plain_in")
        with col2:
            rsa_pub_in = st.text_area("Public Key Penerima (PEM):", value=st.session_state["rsa_pub"], height=120, key="rsa_pub_use")

        if st.button("Enkripsi dengan RSA", type="primary", key="btn_rsa_enc"):
            if rsa_plain and rsa_pub_in:
                try:
                    data_bytes = rsa_plain.encode('utf-8')
                    enc_bytes = rsa_encrypt(data_bytes, rsa_pub_in)
                    b64_res = base64.b64encode(enc_bytes).decode('ascii')
                    st.success("Teks berhasil dienkripsi!")
                    st.markdown("**Hasil Ciphertext (Base64):**")
                    st.code(b64_res, language="text")
                except Exception as e:
                    st.error(f"Gagal melakukan enkripsi RSA: {e}")
            else:
                st.warning("Mohon isi plaintext dan public key.")

    with tab_dec:
        col1, col2 = st.columns(2)
        with col1:
            rsa_cipher_in = st.text_area("Ciphertext (Base64):", height=120, key="rsa_cipher_use")
        with col2:
            rsa_priv_in = st.text_area("Private Key Pemilik (PEM):", value=st.session_state["rsa_priv"], height=120, key="rsa_priv_use")

        if st.button("Dekripsi dengan RSA", type="primary", key="btn_rsa_dec"):
            if rsa_cipher_in and rsa_priv_in:
                try:
                    clean_b64 = "".join(rsa_cipher_in.split())
                    enc_bytes = base64.b64decode(clean_b64)
                    dec_bytes = rsa_decrypt(enc_bytes, rsa_priv_in)
                    plain_res = dec_bytes.decode('utf-8')
                    st.success("Ciphertext berhasil didekripsi!")
                    st.text_area("Plaintext Asli:", value=plain_res, height=120)
                except Exception as e:
                    st.error(f"Gagal melakukan dekripsi RSA: {e}. Pastikan ciphertext dan private key cocok.")
            else:
                st.warning("Mohon isi ciphertext dan private key.")


# ==============================================================================
# HALAMAN 5: SUPER ENKRIPSI
# ==============================================================================
elif menu == "5. Super Enkripsi":
    st.markdown('<div class="main-title">🚀 Super Enkripsi (Multi-Layer Pipeline)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Penggabungan 4 lapis algoritma kriptografi (Caesar + Vigenère + RC4 + RSA) untuk perlindungan mendalam (Defense in Depth).</div>', unsafe_allow_html=True)

    # Info alur pipeline
    st.info(
        "**Alur Pipeline:**\n"
        "Input Teks ➡️ **1. Caesar** ➡️ **2. Vigenère** ➡️ **3. RC4 Stream** ➡️ **4. RSA Public-Key** ➡️ **Ciphertext Akhir (Base64)**"
    )

    # Auto-generate keys if empty
    if not st.session_state["rsa_pub"] or not st.session_state["rsa_priv"]:
        pub_default, priv_default = generate_rsa_keys(2048)
        st.session_state["rsa_pub"] = pub_default
        st.session_state["rsa_priv"] = priv_default

    tab_enc, tab_dec = st.tabs(["🚀 Eksekusi Super Enkripsi", "🔄 Eksekusi Super Dekripsi"])

    # ------------------------- TAB SUPER ENKRIPSI -------------------------
    with tab_enc:
        st.subheader("1. Konfigurasi Semua Kunci")
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            s_caesar_shift = st.number_input("1️⃣ Caesar Shift:", min_value=1, max_value=25, value=7, key="super_caesar_shift")
        with col_k2:
            s_vig_key = st.text_input("2️⃣ Vigenère Key:", value="NUSANTARA", key="super_vig_key")
        with col_k3:
            s_rc4_key = st.text_input("3️⃣ RC4 Secret Key:", value="KunciStreamRC42026", type="password", key="super_rc4_key")

        st.markdown("**4️⃣ Kunci RSA (Public Key untuk Enkripsi)**")
        col_rsa_btn, col_rsa_area = st.columns([1, 4])
        with col_rsa_btn:
            if st.button("Generate Kunci RSA Baru", key="btn_super_gen_rsa"):
                with st.spinner("Membuat kunci RSA 2048-bit..."):
                    pub, priv = generate_rsa_keys(2048)
                    st.session_state["rsa_pub"] = pub
                    st.session_state["rsa_priv"] = priv
                    st.success("Kunci RSA baru siap digunakan!")
        with col_rsa_area:
            s_rsa_pub = st.text_area("RSA Public Key (PEM):", value=st.session_state["rsa_pub"], height=90, key="super_rsa_pub_in")

        st.subheader("2. Masukkan Pesan Terang")
        super_plain = st.text_area(
            "Teks Pesan:",
            value="Dokumen rahasia intelijen negara: koordinat operasi telah dipindahkan ke sektor 7.",
            height=100,
            key="super_plain_in"
        )

        if st.button("Mulai Proses Super Enkripsi", type="primary", use_container_width=True, key="btn_run_super_enc"):
            if super_plain and s_vig_key and s_rc4_key and s_rsa_pub:
                try:
                    with st.spinner("Memproses enkripsi 4 tahap..."):
                        enc_details = super_encrypt(
                            super_plain,
                            int(s_caesar_shift),
                            s_vig_key,
                            s_rc4_key,
                            s_rsa_pub
                        )

                    st.session_state["super_last_ciphertext"] = enc_details["final_ciphertext"]
                    st.success("🎉 Super Enkripsi Berhasil Diselesaikan!")

                    st.markdown("### 🏆 Hasil Akhir Ciphertext (Base64):")
                    st.code(enc_details["final_ciphertext"], language="text")

                    # Step by step visualization
                    st.markdown("### 🔬 Tahapan Detail Transformasi (Step-by-Step):")

                    with st.expander("Langkah 1: Caesar Cipher (Pergeseran Karakter)", expanded=True):
                        st.write(f"**Plaintext:** `{enc_details['step0_plaintext']}`")
                        st.write(f"**Shift (+{s_caesar_shift}):** `{enc_details['step1_caesar']}`")

                    with st.expander("Langkah 2: Vigenère Cipher (Substitusi Polialfabetik)", expanded=True):
                        st.write(f"**Input dari Caesar:** `{enc_details['step1_caesar']}`")
                        st.write(f"**Kata Kunci:** `{s_vig_key}`")
                        st.write(f"**Hasil Vigenère:** `{enc_details['step2_vigenere']}`")

                    with st.expander("Langkah 3: RC4 Stream Cipher (Bitwise Keystream XOR)", expanded=True):
                        st.write(f"**Input Teks UTF-8:** `{enc_details['step2_vigenere']}`")
                        st.write(f"**RC4 Key:** `{s_rc4_key}`")
                        st.write(f"**Hasil RC4 (Hexadecimal):**")
                        st.code(enc_details['step3_rc4_hex'], language="text")
                        st.write(f"**Hasil RC4 (Base64):** `{enc_details['step3_rc4_b64']}`")

                    with st.expander("Langkah 4: RSA PKCS#1 OAEP Asymmetric Encryption (Kunci Publik)", expanded=True):
                        st.write(f"**Input Byte RC4:** {len(enc_details['step3_rc4_bytes'])} bytes")
                        st.write(f"**Ciphertext RSA (Hexadecimal):**")
                        st.code(enc_details['step4_rsa_hex'], language="text")
                        st.write(f"**Ciphertext Akhir (Base64):**")
                        st.code(enc_details['step4_rsa_b64'], language="text")

                except Exception as e:
                    st.error(f"Gagal menjalankan Super Enkripsi: {e}")
            else:
                st.warning("Mohon lengkapi semua parameter teks dan kunci.")

    # ------------------------- TAB SUPER DEKRIPSI -------------------------
    with tab_dec:
        st.subheader("1. Kunci Pembuka Sandi (Dekripsi)")
        col_dk1, col_dk2, col_dk3 = st.columns(3)
        with col_dk1:
            sd_caesar_shift = st.number_input("1️⃣ Caesar Shift:", min_value=1, max_value=25, value=7, key="super_dec_caesar_shift")
        with col_dk2:
            sd_vig_key = st.text_input("2️⃣ Vigenère Key:", value="NUSANTARA", key="super_dec_vig_key")
        with col_dk3:
            sd_rc4_key = st.text_input("3️⃣ RC4 Secret Key:", value="KunciStreamRC42026", type="password", key="super_dec_rc4_key")

        st.markdown("**4️⃣ Kunci RSA (Private Key untuk Dekripsi)**")
        sd_rsa_priv = st.text_area("RSA Private Key (PEM):", value=st.session_state["rsa_priv"], height=90, key="super_dec_rsa_priv_in")

        st.subheader("2. Masukkan Ciphertext Super Enkripsi (Base64)")
        default_cipher_val = st.session_state.get("super_last_ciphertext", "")
        sd_cipher_in = st.text_area(
            "Ciphertext (Base64):",
            value=default_cipher_val,
            placeholder="Tempel ciphertext Base64 hasil Super Enkripsi di sini...",
            height=120,
            key="super_dec_cipher_in"
        )

        if st.button("Mulai Proses Super Dekripsi", type="primary", use_container_width=True, key="btn_run_super_dec"):
            if sd_cipher_in and sd_vig_key and sd_rc4_key and sd_rsa_priv:
                try:
                    with st.spinner("Membalikkan proses enkripsi 4 tahap..."):
                        dec_details = super_decrypt(
                            sd_cipher_in,
                            int(sd_caesar_shift),
                            sd_vig_key,
                            sd_rc4_key,
                            sd_rsa_priv
                        )

                    st.success("🎉 Super Dekripsi Berhasil! Pesan asli berhasil dipulihkan.")
                    st.markdown("### 📜 Pesan Asli (Plaintext):")
                    st.info(dec_details["final_plaintext"])

                    st.markdown("### 🔬 Tahapan Detail Pembalikan (Step-by-Step):")

                    with st.expander("Langkah 1: RSA Asymmetric Decryption (Memulihkan Byte RC4)", expanded=True):
                        st.write(f"**RC4 Ciphertext Pulih (Hex):**")
                        st.code(dec_details['step1_rsa_decrypted_hex'], language="text")

                    with st.expander("Langkah 2: RC4 Stream Decryption (Memulihkan Teks Vigenère)", expanded=True):
                        st.write(f"**Teks Vigenère Terbuka:** `{dec_details['step2_rc4_decrypted_text']}`")

                    with st.expander("Langkah 3: Vigenère Decryption (Memulihkan Teks Caesar)", expanded=True):
                        st.write(f"**Teks Caesar Terbuka:** `{dec_details['step3_vigenere_decrypted_text']}`")

                    with st.expander("Langkah 4: Caesar Decryption (Memulihkan Plaintext Awal)", expanded=True):
                        st.write(f"**Plaintext Asli (Shift -{sd_caesar_shift}):** `{dec_details['step4_caesar_decrypted_plaintext']}`")

                except Exception as e:
                    st.error(f"Gagal melakukan Super Dekripsi: {e}. Pastikan seluruh kunci cocok dan ciphertext tidak terpotong.")
            else:
                st.warning("Mohon lengkapi ciphertext dan semua kunci pembuka.")
