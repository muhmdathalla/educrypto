"""
Modul Kriptografi Edukatif
Implementasi:
1. Caesar Cipher (Klasik - Substitusi Monoalfabetik)
2. Vigenère Cipher (Klasik - Substitusi Polialfabetik)
3. RC4 Cipher (Modern - Stream Cipher Simetris)
4. RSA Cipher (Modern - Kriptografi Asimetris PKCS1_OAEP)
5. Super Enkripsi & Dekripsi (Pipeline Berantai Multi-layer)
"""

import base64
import binascii
from typing import Dict, Any, Tuple
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


# ==============================================================================
# 1. CAESAR CIPHER
# ==============================================================================
def encrypt_caesar(text: str, shift: int) -> str:
    """
    Enkripsi teks menggunakan Caesar Cipher.
    Hanya karakter alfabet (A-Z, a-z) yang digeser, karakter lain tetap dipertahankan.
    """
    shift = shift % 26
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            base = ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        elif 'A' <= char <= 'Z':
            base = ord('A')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return "".join(result)


def decrypt_caesar(text: str, shift: int) -> str:
    """
    Dekripsi teks Caesar Cipher (pergeseran berlawanan arah).
    """
    return encrypt_caesar(text, -shift)


# ==============================================================================
# 2. VIGENÈRE CIPHER
# ==============================================================================
def _clean_key(key: str) -> str:
    """Menyaring kunci Vigenère hanya berisi huruf latin."""
    cleaned = "".join([c.upper() for c in key if c.isalpha()])
    if not cleaned:
        raise ValueError("Kunci Vigenère harus mengandung minimal 1 karakter alfabet (A-Z).")
    return cleaned


def encrypt_vigenere(text: str, key: str) -> str:
    """
    Enkripsi teks menggunakan Vigenère Cipher.
    Karakter non-alfabet tidak diubah dan tidak mengonsumsi indeks kunci.
    """
    cleaned_key = _clean_key(key)
    result = []
    key_idx = 0
    key_len = len(cleaned_key)

    for char in text:
        if 'a' <= char <= 'z':
            shift = ord(cleaned_key[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            key_idx += 1
        elif 'A' <= char <= 'Z':
            shift = ord(cleaned_key[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            key_idx += 1
        else:
            result.append(char)
    return "".join(result)


def decrypt_vigenere(text: str, key: str) -> str:
    """
    Dekripsi teks Vigenère Cipher.
    """
    cleaned_key = _clean_key(key)
    result = []
    key_idx = 0
    key_len = len(cleaned_key)

    for char in text:
        if 'a' <= char <= 'z':
            shift = ord(cleaned_key[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
            key_idx += 1
        elif 'A' <= char <= 'Z':
            shift = ord(cleaned_key[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
            key_idx += 1
        else:
            result.append(char)
    return "".join(result)


# ==============================================================================
# 3. RC4 CIPHER (STREAM CIPHER)
# ==============================================================================
def rc4_ksa(key: bytes) -> list:
    """Key-Scheduling Algorithm (KSA) untuk inisialisasi state S-box."""
    s = list(range(256))
    j = 0
    key_len = len(key)
    if key_len == 0:
        raise ValueError("Kunci RC4 tidak boleh kosong.")
    for i in range(256):
        j = (j + s[i] + key[i % key_len]) % 256
        s[i], s[j] = s[j], s[i]
    return s


def rc4_prga(s: list):
    """Pseudo-Random Generation Algorithm (PRGA) generator."""
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        k = s[(s[i] + s[j]) % 256]
        yield k


def rc4_crypt(data: bytes, key: bytes) -> bytes:
    """
    Enkripsi/Dekripsi RC4. Karena RC4 menggunakan operasi XOR simetris,
    fungsi enkripsi dan dekripsi adalah sama persis.
    """
    if not key:
        raise ValueError("Kunci RC4 tidak boleh kosong.")
    s = rc4_ksa(key)
    keystream = rc4_prga(s)
    return bytes([b ^ next(keystream) for b in data])


# ==============================================================================
# 4. RSA CIPHER (ASYMMETRIC PUBLIC-KEY)
# ==============================================================================
def generate_rsa_keys(bits: int = 2048) -> Tuple[str, str]:
    """
    Membangkitkan pasangan kunci RSA (Public & Private Key) dalam format PEM.
    """
    key = RSA.generate(bits)
    private_pem = key.export_key().decode('utf-8')
    public_pem = key.publickey().export_key().decode('utf-8')
    return public_pem, private_pem


def rsa_encrypt(data: bytes, public_key_pem: str) -> bytes:
    """
    Enkripsi data byte menggunakan RSA PKCS1_OAEP.
    Mendukung chunking otomatis jika ukuran data melebihi batas per-blok RSA.
    """
    try:
        rsa_key = RSA.import_key(public_key_pem)
    except Exception as e:
        raise ValueError(f"Public Key RSA tidak valid: {e}")

    cipher = PKCS1_OAEP.new(rsa_key)
    key_bytes = rsa_key.size_in_bytes()
    # Batas plaintext OAEP (dengan SHA-1 default): key_size - 42 bytes
    max_chunk = key_bytes - 42

    encrypted_chunks = []
    for i in range(0, len(data), max_chunk):
        chunk = data[i:i + max_chunk]
        encrypted_chunks.append(cipher.encrypt(chunk))

    return b"".join(encrypted_chunks)


def rsa_decrypt(ciphertext: bytes, private_key_pem: str) -> bytes:
    """
    Dekripsi data ciphertext byte menggunakan RSA PKCS1_OAEP.
    Mendukung chunking otomatis.
    """
    try:
        rsa_key = RSA.import_key(private_key_pem)
    except Exception as e:
        raise ValueError(f"Private Key RSA tidak valid: {e}")

    cipher = PKCS1_OAEP.new(rsa_key)
    key_bytes = rsa_key.size_in_bytes()

    if len(ciphertext) % key_bytes != 0:
        raise ValueError(f"Panjang ciphertext ({len(ciphertext)} byte) bukan kelipatan ukuran blok RSA ({key_bytes} byte).")

    decrypted_chunks = []
    for i in range(0, len(ciphertext), key_bytes):
        chunk = ciphertext[i:i + key_bytes]
        decrypted_chunks.append(cipher.decrypt(chunk))

    return b"".join(decrypted_chunks)


# ==============================================================================
# 5. SUPER ENKRIPSI & DEKRIPSI
# ==============================================================================
def super_encrypt(
    plaintext: str,
    caesar_shift: int,
    vigenere_key: str,
    rc4_key: str,
    rsa_public_pem: str
) -> Dict[str, Any]:
    """
    Melakukan Super Enkripsi berantai:
    Plaintext -> Caesar -> Vigenere -> RC4 -> RSA -> Ciphertext (Base64/Hex).
    Mengembalikan dict berisi hasil akhir dan setiap langkah intermediate.
    """
    # Langkah 1: Caesar Cipher
    caesar_output = encrypt_caesar(plaintext, caesar_shift)

    # Langkah 2: Vigenère Cipher
    vigenere_output = encrypt_vigenere(caesar_output, vigenere_key)

    # Langkah 3: RC4 Stream Cipher
    rc4_input_bytes = vigenere_output.encode('utf-8')
    rc4_key_bytes = rc4_key.encode('utf-8')
    rc4_output_bytes = rc4_crypt(rc4_input_bytes, rc4_key_bytes)
    rc4_hex = rc4_output_bytes.hex()
    rc4_b64 = base64.b64encode(rc4_output_bytes).decode('ascii')

    # Langkah 4: RSA Asymmetric Encryption
    rsa_output_bytes = rsa_encrypt(rc4_output_bytes, rsa_public_pem)
    rsa_b64 = base64.b64encode(rsa_output_bytes).decode('ascii')
    rsa_hex = rsa_output_bytes.hex()

    return {
        "step0_plaintext": plaintext,
        "step1_caesar": caesar_output,
        "step2_vigenere": vigenere_output,
        "step3_rc4_bytes": rc4_output_bytes,
        "step3_rc4_hex": rc4_hex,
        "step3_rc4_b64": rc4_b64,
        "step4_rsa_bytes": rsa_output_bytes,
        "step4_rsa_hex": rsa_hex,
        "step4_rsa_b64": rsa_b64,
        "final_ciphertext": rsa_b64
    }


def super_decrypt(
    ciphertext_b64: str,
    caesar_shift: int,
    vigenere_key: str,
    rc4_key: str,
    rsa_private_pem: str
) -> Dict[str, Any]:
    """
    Melakukan Super Dekripsi dengan membalik urutan:
    Ciphertext (Base64) -> RSA Decrypt -> RC4 Decrypt -> Vigenère Decrypt -> Caesar Decrypt -> Plaintext Asli.
    """
    # Persiapan: Decode Base64 ciphertext
    try:
        clean_b64 = "".join(ciphertext_b64.split())
        rsa_input_bytes = base64.b64decode(clean_b64)
    except Exception as e:
        raise ValueError(f"Format Base64 ciphertext tidak valid: {e}")

    # Langkah 1: RSA Decrypt
    rc4_cipher_bytes = rsa_decrypt(rsa_input_bytes, rsa_private_pem)
    rc4_hex = rc4_cipher_bytes.hex()
    rc4_b64 = base64.b64encode(rc4_cipher_bytes).decode('ascii')

    # Langkah 2: RC4 Decrypt
    rc4_key_bytes = rc4_key.encode('utf-8')
    vigenere_bytes = rc4_crypt(rc4_cipher_bytes, rc4_key_bytes)
    try:
        vigenere_output = vigenere_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Gagal mendekode byte hasil RC4 ke teks UTF-8. Pastikan kunci RC4 benar.")

    # Langkah 3: Vigenère Decrypt
    caesar_output = decrypt_vigenere(vigenere_output, vigenere_key)

    # Langkah 4: Caesar Decrypt
    recovered_plaintext = decrypt_caesar(caesar_output, caesar_shift)

    return {
        "step0_ciphertext_b64": ciphertext_b64,
        "step1_rsa_decrypted_bytes": rc4_cipher_bytes,
        "step1_rsa_decrypted_hex": rc4_hex,
        "step1_rsa_decrypted_b64": rc4_b64,
        "step2_rc4_decrypted_text": vigenere_output,
        "step3_vigenere_decrypted_text": caesar_output,
        "step4_caesar_decrypted_plaintext": recovered_plaintext,
        "final_plaintext": recovered_plaintext
    }
