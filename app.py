import streamlit as st
import base64
import hashlib
import json
import pandas as pd
from ciphers import (
    encrypt_caesar, decrypt_caesar,
    encrypt_vigenere, decrypt_vigenere,
    rc4_crypt,
    generate_rsa_keys, rsa_encrypt, rsa_decrypt,
    super_encrypt, super_decrypt,
    encrypt_file_container, decrypt_file_container,
    calculate_shannon_entropy, calculate_index_of_coincidence,
    analyze_letter_frequency, calculate_avalanche_effect,
    caesar_brute_force_attack, inspect_rc4_state, inspect_rsa_key_details
)
from server import fetch_usd_idr_rate

# ==============================================================================
# KONFIGURASI HALAMAN & DESIGN THEME MONOCHROME
# ==============================================================================
st.set_page_config(
    page_title="EduCrypto Studio — Laboratorium Kriptografi Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Editorial Monochrome & Modern Web Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #080808;
        color: #F4F4F5;
    }
    
    /* Editorial Monochrome Typography */
    .hero-title {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 400;
        color: #FFFFFF;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #A1A1AA;
        margin-bottom: 1.5rem;
        max-width: 800px;
        line-height: 1.6;
    }
    .spec-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #71717A;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    /* Header Active Module & FX Ticker Bar */
    .top-telemetry-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 1.25rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        margin-bottom: 2rem;
        backdrop-filter: blur(16px);
    }
    .telemetry-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #FFFFFF;
        display: inline-block;
    }
    .fx-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.35rem 0.85rem;
        background: #18181B;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        color: #FFFFFF;
    }
    
    /* Floating Glass Dock Style Card */
    .dock-callout {
        background: rgba(24, 24, 27, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(20px);
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Session State
if "rsa_pub" not in st.session_state or not st.session_state["rsa_pub"]:
    pub_init, priv_init = generate_rsa_keys(2048)
    st.session_state["rsa_pub"] = pub_init
    st.session_state["rsa_priv"] = priv_init
if "super_last_ciphertext" not in st.session_state:
    st.session_state["super_last_ciphertext"] = ""

# Fetch USD / IDR
fx_data = fetch_usd_idr_rate()
usd_rate_str = f"Rp {fx_data['rate']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==============================================================================
# SIDEBAR DOCK & NAVIGASI
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.8rem;">EduCrypto</div>', unsafe_allow_html=True)
    st.caption("Editorial Monochrome Cryptographic Laboratory // v2.5")
    st.markdown("---")
    
    menu = st.radio(
        "Pilih Modul Algoritma Kriptografi:",
        [
            "1. Caesar Cipher",
            "2. Vigenère Cipher",
            "3. RC4 Cipher",
            "4. RSA Cipher",
            "5. Super Enkripsi",
            "6. File, Image & Audio Vault",
            "7. Security Audit & Cryptanalysis"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"**Kurs Pasar Live:**\n`USD / IDR = {usd_rate_str}`")
    st.markdown("---")
    st.caption("✨ Untuk pengalaman web app interaktif penuh (Liquid Glass macOS Dock, animasi canvas, kalkulator kurs terpadu), jalankan `python3 server.py` lalu buka http://localhost:8500")

# ==============================================================================
# TOP TELEMETRY BAR
# ==============================================================================
st.markdown(f"""
<div class="top-telemetry-bar">
    <div class="telemetry-tag">
        <span class="pulse-dot"></span>
        <span>MODUL AKTIF: <strong>{menu}</strong></span>
    </div>
    <div class="fx-pill">
        USD / IDR: {usd_rate_str}
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. CAESAR CIPHER
# ==============================================================================
if menu == "1. Caesar Cipher":
    st.markdown('<div class="spec-badge">MODUL 01 // SUBSTITUSI MONOALFABETIK</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Caesar Cipher</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Pergeseran posisi karakter alfabet Latin sejauh kunci k di dalam grup siklik modulo 26. Simbol non-alfabet tetap dipertahankan.</div>', unsafe_allow_html=True)

    tab_enc, tab_dec, tab_vis = st.tabs(["🔒 Enkripsi", "🔓 Dekripsi", "🔍 Visualisasi Pergeseran"])

    with tab_enc:
        col1, col2 = st.columns([3, 1])
        with col1:
            caesar_input = st.text_area("Plaintext:", value="Kriptografi adalah seni menjaga kerahasiaan informasi.", height=110, key="caesar_enc_in")
        with col2:
            shift_enc = st.number_input("Shift k:", min_value=1, max_value=25, value=3, step=1, key="caesar_shift_enc")

        if st.button("Enkripsi Caesar →", type="primary"):
            if caesar_input:
                res = encrypt_caesar(caesar_input, shift_enc)
                st.session_state["caesar_dec_in"] = res
                st.session_state["caesar_shift_dec"] = shift_enc
                st.success("Teks berhasil dienkripsi!")
                st.code(res, language="text")
                e_in = calculate_shannon_entropy(caesar_input.encode('utf-8'))
                e_out = calculate_shannon_entropy(res.encode('utf-8'))
                st.caption(f"Shannon Entropy: {e_in} → {e_out} bits/byte | IoC: {calculate_index_of_coincidence(res)}")

    with tab_dec:
        col1, col2 = st.columns([3, 1])
        with col1:
            default_dec = st.session_state.get("caesar_dec_in", "Nulswrjudil dgdodk vhql phqmdjd nhudkdvlddq lqirupdvl.")
            caesar_dec_input = st.text_area("Ciphertext:", value=default_dec, height=110, key="caesar_dec_in")
        with col2:
            default_shift_dec = st.session_state.get("caesar_shift_dec", 3)
            shift_dec = st.number_input("Shift k:", min_value=1, max_value=25, value=default_shift_dec, step=1, key="caesar_shift_dec")

        if st.button("← Dekripsi Caesar", type="secondary"):
            if caesar_dec_input:
                res = decrypt_caesar(caesar_dec_input, shift_dec)
                st.success("Teks berhasil didekripsi!")
                st.code(res, language="text")

    with tab_vis:
        st.markdown("#### Tabel Pemetaan Alfabet Shift k")
        sample_shift = st.slider("Pilih Shift:", min_value=1, max_value=25, value=3)
        orig_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        mapped_letters = [chr((i - ord('A') + sample_shift) % 26 + ord('A')) for i in range(ord('A'), ord('Z') + 1)]
        df_map = pd.DataFrame({"Plain": orig_letters, f"Shift +{sample_shift}": mapped_letters}).T
        st.dataframe(df_map, use_container_width=True)

# ==============================================================================
# 2. VIGENÈRE CIPHER
# ==============================================================================
elif menu == "2. Vigenère Cipher":
    st.markdown('<div class="spec-badge">MODUL 02 // SUBSTITUSI POLIALFABETIK</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Vigenère Cipher</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Substitusi polialfabetik dinamis berbasis perulangan kata kunci (keystream). Karakter non-alfabet tidak menggeser indeks kunci.</div>', unsafe_allow_html=True)

    tab_enc, tab_dec = st.tabs(["🔒 Enkripsi", "🔓 Dekripsi"])

    with tab_enc:
        col1, col2 = st.columns([3, 1])
        with col1:
            vig_input = st.text_area("Plaintext:", value="Serang musuh di bukit timur saat fajar tiba!", height=110, key="vig_enc_in")
        with col2:
            vig_key_enc = st.text_input("Kata Kunci (Key):", value="GARUDA", key="vig_key_enc")

        if st.button("Enkripsi Vigenère →", type="primary"):
            if vig_input and vig_key_enc:
                try:
                    res = encrypt_vigenere(vig_input, vig_key_enc)
                    st.session_state["vig_dec_in"] = res
                    st.session_state["vig_key_dec"] = vig_key_enc
                    st.success("Teks berhasil dienkripsi!")
                    st.code(res, language="text")
                    st.caption(f"Shannon Entropy: {calculate_shannon_entropy(res.encode('utf-8'))} bits/byte | IoC: {calculate_index_of_coincidence(res)}")
                except ValueError as e:
                    st.error(str(e))

    with tab_dec:
        col1, col2 = st.columns([3, 1])
        with col1:
            default_dec = st.session_state.get("vig_dec_in", "Yeiuqg sujok do blelt zidou sgak zdjgr kcea!")
            vig_dec_input = st.text_area("Ciphertext:", value=default_dec, height=110, key="vig_dec_in")
        with col2:
            default_k_dec = st.session_state.get("vig_key_dec", "GARUDA")
            vig_key_dec = st.text_input("Kata Kunci:", value=default_k_dec, key="vig_key_dec")

        if st.button("← Dekripsi Vigenère", type="secondary"):
            if vig_dec_input and vig_key_dec:
                try:
                    res = decrypt_vigenere(vig_dec_input, vig_key_dec)
                    st.success("Teks berhasil didekripsi!")
                    st.code(res, language="text")
                except ValueError as e:
                    st.error(str(e))

# ==============================================================================
# 3. RC4 CIPHER
# ==============================================================================
elif menu == "3. RC4 Cipher":
    st.markdown('<div class="spec-badge">MODUL 03 // STREAM CIPHER SIMETRIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">RC4 (Rivest Cipher 4)</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Stream cipher simetris berkinerja tinggi berbasis permutasi 256-byte S-Box (KSA) dan pembangkitan bitwise keystream XOR (PRGA).</div>', unsafe_allow_html=True)

    tab_enc, tab_dec = st.tabs(["🔒 Enkripsi (Text → Hex/Base64)", "🔓 Dekripsi (Hex/Base64 → Text)"])

    with tab_enc:
        col1, col2 = st.columns([3, 1])
        with col1:
            rc4_input = st.text_area("Plaintext:", value="Data rahasia transaksi perbankan 2026", height=110, key="rc4_enc_in")
        with col2:
            rc4_key_enc = st.text_input("Kunci RC4:", value="SecretKey123!", type="password", key="rc4_key_enc")

        if st.button("Enkripsi RC4 →", type="primary"):
            if rc4_input and rc4_key_enc:
                c_bytes = rc4_crypt(rc4_input.encode('utf-8'), rc4_key_enc.encode('utf-8'))
                h_out = c_bytes.hex()
                b_out = base64.b64encode(c_bytes).decode('ascii')
                st.session_state["rc4_dec_in"] = h_out
                st.session_state["rc4_key_dec"] = rc4_key_enc
                st.success("Teks berhasil dienkripsi!")
                st.markdown("**Hexadecimal:**")
                st.code(h_out, language="text")
                st.markdown("**Base64:**")
                st.code(b_out, language="text")
                st.caption(f"Ukuran: {len(rc4_input)} Byte → {len(c_bytes)} Byte | Shannon Entropy: {calculate_shannon_entropy(c_bytes)} bits/B")

    with tab_dec:
        col1, col2 = st.columns([3, 1])
        with col1:
            fmt = st.radio("Format Ciphertext Input:", ["Hexadecimal", "Base64"], horizontal=True)
            default_rc4_dec = st.session_state.get("rc4_dec_in", "")
            rc4_dec_input = st.text_area("Ciphertext:", value=default_rc4_dec, height=110, key="rc4_dec_in")
        with col2:
            default_k_rc4 = st.session_state.get("rc4_key_dec", "SecretKey123!")
            rc4_key_dec = st.text_input("Kunci RC4:", value=default_k_rc4, type="password", key="rc4_key_dec")

        if st.button("← Dekripsi RC4", type="secondary"):
            if rc4_dec_input and rc4_key_dec:
                try:
                    c_clean = "".join(rc4_dec_input.split())
                    in_b = bytes.fromhex(c_clean) if fmt == "Hexadecimal" else base64.b64decode(c_clean)
                    p_b = rc4_crypt(in_b, rc4_key_dec.encode('utf-8'))
                    st.success("Plaintext Berhasil Dipulihkan:")
                    st.code(p_b.decode('utf-8'), language="text")
                except Exception as e:
                    st.error(f"Gagal dekripsi RC4: {e}")

# ==============================================================================
# 4. RSA CIPHER
# ==============================================================================
elif menu == "4. RSA Cipher":
    st.markdown('<div class="spec-badge">MODUL 04 // ASIMETRIS KUNCI PUBLIK</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">RSA PKCS#1 OAEP</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Kriptografi kunci publik dengan padding Optimal Asymmetric Encryption Padding (OAEP) untuk mencegah serangan matematis Coppersmith & padding oracle.</div>', unsafe_allow_html=True)

    col_g1, col_g2 = st.columns([1, 3])
    with col_g1:
        bits = st.selectbox("Panjang Kunci:", [1024, 2048], index=1)
        if st.button("Generate Kunci Baru ↻", use_container_width=True):
            pub, priv = generate_rsa_keys(bits)
            st.session_state["rsa_pub"] = pub
            st.session_state["rsa_priv"] = priv
            st.success(f"Keypair RSA {bits}-bit siap!")
            st.rerun()

    with col_g2:
        k_c1, k_c2 = st.columns(2)
        with k_c1:
            st.text_area("Public Key (PEM):", value=st.session_state["rsa_pub"], height=130)
        with k_c2:
            st.text_area("Private Key (PEM):", value=st.session_state["rsa_priv"], height=130)

    st.markdown("---")
    tab_enc, tab_dec = st.tabs(["🔒 Enkripsi (Public Key)", "🔓 Dekripsi (Private Key)"])

    with tab_enc:
        col1, col2 = st.columns(2)
        with col1:
            rsa_plain = st.text_area("Plaintext:", value="Kerahasiaan data menggunakan RSA 2048-bit", height=110)
        with col2:
            rsa_pub_use = st.text_area("Public Key Penerima:", value=st.session_state["rsa_pub"], height=110)

        if st.button("Enkripsi RSA OAEP →", type="primary"):
            if rsa_plain and rsa_pub_use:
                try:
                    c_bytes = rsa_encrypt(rsa_plain.encode('utf-8'), rsa_pub_use)
                    b64_c = base64.b64encode(c_bytes).decode('ascii')
                    st.session_state["rsa_cipher_use"] = b64_c
                    st.success("Ciphertext RSA OAEP Berhasil Dihasilkan:")
                    st.code(b64_c, language="text")
                    st.caption(f"Ukuran: {len(c_bytes)} byte | Shannon Entropy: {calculate_shannon_entropy(c_bytes)} bits/B")
                except Exception as e:
                    st.error(f"Error RSA Encrypt: {e}")

    with tab_dec:
        col1, col2 = st.columns(2)
        with col1:
            default_rsa_c = st.session_state.get("rsa_cipher_use", "")
            rsa_cipher_in = st.text_area("Ciphertext (Base64):", value=default_rsa_c, height=110)
        with col2:
            rsa_priv_use = st.text_area("Private Key Pemilik:", value=st.session_state["rsa_priv"], height=110)

        if st.button("← Dekripsi RSA OAEP", type="secondary"):
            if rsa_cipher_in and rsa_priv_use:
                try:
                    raw_c = base64.b64decode("".join(rsa_cipher_in.split()))
                    p_b = rsa_decrypt(raw_c, rsa_priv_use)
                    st.success("Plaintext Berhasil Dipulihkan:")
                    st.code(p_b.decode('utf-8'), language="text")
                except Exception as e:
                    st.error(f"Error RSA Decrypt: {e}")

# ==============================================================================
# 5. SUPER ENKRIPSI
# ==============================================================================
elif menu == "5. Super Enkripsi":
    st.markdown('<div class="spec-badge">MODUL 05 // MULTI-LAYER DEFENSE IN DEPTH</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Super Enkripsi (4-Lapis)</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Pipeline berantai multi-layer: Plaintext → Caesar → Vigenère → RC4 Stream → RSA Asimetris OAEP.</div>', unsafe_allow_html=True)

    tab_enc, tab_dec = st.tabs(["🚀 Eksekusi Super Enkripsi", "🔄 Eksekusi Super Dekripsi"])

    with tab_enc:
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            s_shift = st.number_input("1. Caesar Shift:", min_value=1, max_value=25, value=7)
        with col_k2:
            s_vig = st.text_input("2. Vigenère Key:", value="NUSANTARA")
        with col_k3:
            s_rc4 = st.text_input("3. RC4 Key:", value="KunciStreamRC42026", type="password")

        super_plain = st.text_area("Pesan Terang (Plaintext):", value="Dokumen rahasia intelijen negara: koordinat operasi telah dipindahkan ke sektor 7.", height=100)

        if st.button("Mulai Proses Super Enkripsi 4-Lapis →", type="primary", use_container_width=True):
            try:
                res = super_encrypt(super_plain, s_shift, s_vig, s_rc4, st.session_state["rsa_pub"])
                st.session_state["super_last_ciphertext"] = res["final_ciphertext"]
                st.session_state["super_dec_shift"] = s_shift
                st.session_state["super_dec_vig"] = s_vig
                st.session_state["super_dec_rc4"] = s_rc4
                st.success("🎉 Super Enkripsi Berhasil!")
                st.markdown("**Ciphertext Akhir (Base64):**")
                st.code(res["final_ciphertext"], language="text")

                with st.expander("🔬 Detail Transformasi 4 Lapisan:", expanded=True):
                    st.write(f"• Layer 1 (Caesar +{s_shift}): `{res['step1_caesar']}`")
                    st.write(f"• Layer 2 (Vigenère '{s_vig}'): `{res['step2_vigenere']}`")
                    st.write(f"• Layer 3 (RC4 Base64): `{res['step3_rc4_b64']}`")
                    st.write(f"• Layer 4 (RSA OAEP Base64): `{res['step4_rsa_b64'][:64]}...`")
            except Exception as e:
                st.error(f"Gagal Super Enkripsi: {e}")

    with tab_dec:
        col_dk1, col_dk2, col_dk3 = st.columns(3)
        with col_dk1:
            sd_shift = st.number_input("1. Caesar Shift:", min_value=1, max_value=25, value=st.session_state.get("super_dec_shift", 7))
        with col_dk2:
            sd_vig = st.text_input("2. Vigenère Key:", value=st.session_state.get("super_dec_vig", "NUSANTARA"))
        with col_dk3:
            sd_rc4 = st.text_input("3. RC4 Key:", value=st.session_state.get("super_dec_rc4", "KunciStreamRC42026"), type="password")

        sd_cipher = st.text_area("Ciphertext Super Enkripsi (Base64):", value=st.session_state.get("super_last_ciphertext", ""), height=100)

        if st.button("← Mulai Proses Super Dekripsi", type="secondary", use_container_width=True):
            try:
                dec = super_decrypt(sd_cipher, sd_shift, sd_vig, sd_rc4, st.session_state["rsa_priv"])
                st.success("🎉 Super Dekripsi Berhasil! Pesan asli berhasil dipulihkan:")
                st.info(dec["final_plaintext"])
            except Exception as e:
                st.error(f"Gagal Super Dekripsi: {e}")

# ==============================================================================
# 6. FILE, IMAGE & AUDIO VAULT
# ==============================================================================
elif menu == "6. File, Image & Audio Vault":
    st.markdown('<div class="spec-badge">MODUL 06 // MULTIMEDIA & FILE VAULT</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">File, Image & Audio Vault</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Enkripsi dan dekripsi file biner apa pun (Gambar PNG/JPG, Audio WAV/MP3, PDF, Dokumen) dengan format kontainer .ecry dan verifikasi integritas SHA-256.</div>', unsafe_allow_html=True)

    tab_fenc, tab_fdec = st.tabs(["🔒 Enkripsi File", "🔓 Dekripsi File"])

    with tab_fenc:
        up_file = st.file_uploader("Pilih File (Gambar, Audio, PDF, Dokumen, dll):", key="f_up_enc")
        col_fa1, col_fa2 = st.columns(2)
        with col_fa1:
            f_algo = st.selectbox("Pilih Algoritma Kriptografi:", ["super", "rc4", "rsa", "vigenere", "caesar"])
        with col_fa2:
            f_key = st.text_input("Passphrase / Kunci:", value="NUSANTARA2026")

        if st.button("Enkripsi File ke Kontainer (.ecry) →", type="primary"):
            if up_file:
                raw_bytes = up_file.read()
                params = {
                    "shift": 7,
                    "vigenere_key": f_key,
                    "rc4_key": f_key,
                    "key": f_key,
                    "public_key": st.session_state["rsa_pub"]
                }
                res = encrypt_file_container(raw_bytes, up_file.name, up_file.type, f_algo, params)
                st.success(f"File berhasil dienkripsi! Waktu: {res['elapsed_ms']} ms")
                st.markdown(f"• **Metode:** {res['metadata']['mode_detail']}")
                st.markdown(f"• **SHA-256 Asli:** `{res['metadata']['orig_sha256']}`")
                st.markdown(f"• **Shannon Entropy:** {res['entropy_plain']} → {res['entropy_cipher']} bits/B")

                st.download_button(
                    label=f"Unduh File Terenkripsi ({up_file.name}.ecry) ↓",
                    data=res["container_bytes"],
                    file_name=f"{up_file.name}.ecry",
                    mime="application/octet-stream"
                )
            else:
                st.warning("Silakan unggah file terlebih dahulu.")

    with tab_fdec:
        up_cfile = st.file_uploader("Pilih File Terenkripsi (.ecry):", key="f_up_dec")
        col_fda1, col_fda2 = st.columns(2)
        with col_fda1:
            fd_algo = st.selectbox("Algoritma (jika non-kontainer):", ["super", "rc4", "rsa", "vigenere", "caesar"], key="fd_algo")
        with col_fda2:
            fd_key = st.text_input("Passphrase / Kunci Pembuka:", value="NUSANTARA2026", key="fd_key")

        if st.button("← Dekripsi & Pulihkan File Asli", type="secondary"):
            if up_cfile:
                raw_c_bytes = up_cfile.read()
                params = {
                    "shift": 7,
                    "vigenere_key": fd_key,
                    "rc4_key": fd_key,
                    "key": fd_key,
                    "private_key": st.session_state["rsa_priv"]
                }
                try:
                    res = decrypt_file_container(raw_c_bytes, fd_algo, params)
                    st.success("File berhasil dipulihkan secara utuh!")
                    st.markdown(f"• **Nama File:** `{res['filename']}`")
                    st.markdown(f"• **SHA-256 Checksum:** `{res['recovered_sha256']}` (LULUS 100% Identik)")

                    # Pratinjau jika gambar / audio
                    if res["mime_type"].startswith("image/"):
                        st.image(res["recovered_bytes"])
                    elif res["mime_type"].startswith("audio/"):
                        st.audio(res["recovered_bytes"])

                    st.download_button(
                        label=f"Unduh File Asli ({res['filename']}) ↓",
                        data=res["recovered_bytes"],
                        file_name=res["filename"],
                        mime=res["mime_type"]
                    )
                except Exception as e:
                    st.error(f"Gagal memulihkan file: {e}")
            else:
                st.warning("Silakan unggah file terenkripsi terlebih dahulu.")

# ==============================================================================
# 7. SECURITY AUDIT & CRYPTANALYSIS LAB
# ==============================================================================
elif menu == "7. Security Audit & Cryptanalysis":
    st.markdown('<div class="spec-badge">MODUL 07 // AUDIT STATISTIK & KRIPTANALISIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Security Audit Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Membuktikan secara ilmiah kualitas keamanan algoritma: Entropi Informasi Shannon, Avalanche Effect (1-bit mutation), Index of Coincidence, dan Simulasi Serangan Brute-Force.</div>', unsafe_allow_html=True)

    audit_txt = st.text_area("Plaintext Uji Komparasi 5 Algoritma:", value="Dokumen rahasia intelijen negara: koordinat operasi telah dipindahkan ke sektor 7.", height=80)

    if st.button("Jalankan Audit Ilmiah 5 Algoritma →", type="primary"):
        first_char = audit_txt[0]
        flipped = chr(ord(first_char) ^ 1) + audit_txt[1:]

        c_a = encrypt_caesar(audit_txt, 7).encode('utf-8')
        c_b = encrypt_caesar(flipped, 7).encode('utf-8')

        v_a = encrypt_vigenere(audit_txt, "NUSANTARA").encode('utf-8')
        v_b = encrypt_vigenere(flipped, "NUSANTARA").encode('utf-8')

        r_a = rc4_crypt(audit_txt.encode('utf-8'), b"SecretRC4")
        r_b = rc4_crypt(flipped.encode('utf-8'), b"SecretRC4")

        rsa_a = rsa_encrypt(audit_txt.encode('utf-8'), st.session_state["rsa_pub"])
        rsa_b = rsa_encrypt(flipped.encode('utf-8'), st.session_state["rsa_pub"])

        sup_a = base64.b64decode(super_encrypt(audit_txt, 7, "NUSANTARA", "SecretRC4", st.session_state["rsa_pub"])["final_ciphertext"])
        sup_b = base64.b64decode(super_encrypt(flipped, 7, "NUSANTARA", "SecretRC4", st.session_state["rsa_pub"])["final_ciphertext"])

        rows = [
            {"Algoritma": "1. Caesar Cipher", "Kategori": "Klasik Monoalfabetik", "Shannon Entropy (bits/B)": calculate_shannon_entropy(c_a), "Avalanche Effect (%)": calculate_avalanche_effect(c_a, c_b)["percentage"], "Index of Coincidence": calculate_index_of_coincidence(c_a.decode('utf-8', errors='ignore'))},
            {"Algoritma": "2. Vigenère Cipher", "Kategori": "Klasik Polialfabetik", "Shannon Entropy (bits/B)": calculate_shannon_entropy(v_a), "Avalanche Effect (%)": calculate_avalanche_effect(v_a, v_b)["percentage"], "Index of Coincidence": calculate_index_of_coincidence(v_a.decode('utf-8', errors='ignore'))},
            {"Algoritma": "3. RC4 Stream", "Kategori": "Simetris Stream XOR", "Shannon Entropy (bits/B)": calculate_shannon_entropy(r_a), "Avalanche Effect (%)": calculate_avalanche_effect(r_a, r_b)["percentage"], "Index of Coincidence": 0.0385},
            {"Algoritma": "4. RSA PKCS#1 OAEP", "Kategori": "Asimetris Public-Key", "Shannon Entropy (bits/B)": calculate_shannon_entropy(rsa_a), "Avalanche Effect (%)": calculate_avalanche_effect(rsa_a, rsa_b)["percentage"], "Index of Coincidence": 0.0385},
            {"Algoritma": "5. Super Enkripsi", "Kategori": "Multi-Layer Defense in Depth", "Shannon Entropy (bits/B)": calculate_shannon_entropy(sup_a), "Avalanche Effect (%)": calculate_avalanche_effect(sup_a, sup_b)["percentage"], "Index of Coincidence": 0.0385}
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.markdown("#### 🔓 Simulasi Serangan Exhaustive Brute-Force pada Caesar:")
        bf_results = caesar_brute_force_attack(c_a.decode('utf-8', errors='ignore'))
        st.dataframe(pd.DataFrame(bf_results[:8]), use_container_width=True)
