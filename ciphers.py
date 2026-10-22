"""
Modul Kriptografi Edukatif & Multimedia (EduCrypto Pro)
Implementasi:
1. Caesar Cipher (Klasik - Substitusi Monoalfabetik & Modulo-256 Byte Shift)
2. Vigenère Cipher (Klasik - Substitusi Polialfabetik & Modulo-256 Byte Vigenère)
3. RC4 Cipher (Modern - Stream Cipher Simetris KSA & PRGA)
4. RSA Cipher (Modern - Kriptografi Asimetris PKCS1_OAEP & Hybrid Envelope)
5. Super Enkripsi & Dekripsi (Pipeline Berantai Multi-layer 4 Tahap)
6. Kriptanalisis, Audit Keamanan (Entropi Shannon, Avalanche Effect, Frekuensi) & Enkripsi File/Gambar/Audio
"""

import base64
import binascii
import hashlib
import hmac
import json
import math
import struct
import time
from collections import Counter
from typing import Dict, Any, Tuple, List, Optional
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes


# ==============================================================================
# 1. CAESAR CIPHER (TEXT - ASLI DIPERTAHANKAN 100%)
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
# 2. VIGENÈRE CIPHER (TEXT - ASLI DIPERTAHANKAN 100%)
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
# 3. RC4 CIPHER (STREAM CIPHER - ASLI DIPERTAHANKAN 100%)
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
# 4. RSA CIPHER (ASYMMETRIC PUBLIC-KEY - ASLI DIPERTAHANKAN 100%)
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

    # [PERBAIKAN] Jika pengguna tidak sengaja memasukkan private key, gunakan komponen public-nya
    if rsa_key.has_private():
        rsa_key = rsa_key.publickey()

    cipher = PKCS1_OAEP.new(rsa_key)
    key_bytes = rsa_key.size_in_bytes()
    # Batas plaintext OAEP (dengan SHA-1 default): key_size - 42 bytes
    max_chunk = key_bytes - 42

    # [PERBAIKAN] Penanganan data byte kosong agar tetap menghasilkan 1 blok ciphertext padding OAEP
    if len(data) == 0:
        return cipher.encrypt(b"")

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

    # [PERBAIKAN] Validasi kunci privat: jika yang dimasukkan adalah Public Key, cegah TypeError PyCryptodome
    if not rsa_key.has_private():
        raise ValueError("Kunci yang dimasukkan adalah Public Key. Dekripsi RSA memerlukan Private Key.")

    cipher = PKCS1_OAEP.new(rsa_key)
    key_bytes = rsa_key.size_in_bytes()

    # [PERBAIKAN] Penanganan ciphertext kosong
    if len(ciphertext) == 0:
        return b""

    if len(ciphertext) % key_bytes != 0:
        raise ValueError(f"Panjang ciphertext ({len(ciphertext)} byte) bukan kelipatan ukuran blok RSA ({key_bytes} byte).")

    decrypted_chunks = []
    for i in range(0, len(ciphertext), key_bytes):
        chunk = ciphertext[i:i + key_bytes]
        decrypted_chunks.append(cipher.decrypt(chunk))

    return b"".join(decrypted_chunks)


# ==============================================================================
# 5. SUPER ENKRIPSI & DEKRIPSI (TEXT - ASLI DIPERTAHANKAN 100%)
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


# ==============================================================================
# 6. ENKRIPSI & DEKRIPSI MULTIMEDIA / FILE BINER (GAMBAR, AUDIO, DOKUMEN, DLL)
# ==============================================================================
def caesar_bytes_encrypt(data: bytes, shift: int) -> bytes:
    """Enkripsi byte-level Modulo-256 Caesar Cipher untuk file biner."""
    shift = shift % 256
    table = bytes((b + shift) % 256 for b in range(256))
    return data.translate(table)


def caesar_bytes_decrypt(data: bytes, shift: int) -> bytes:
    """Dekripsi byte-level Modulo-256 Caesar Cipher untuk file biner."""
    return caesar_bytes_encrypt(data, -shift)


def vigenere_bytes_encrypt(data: bytes, key: str) -> bytes:
    """Enkripsi byte-level Modulo-256 Vigenère Cipher untuk file biner."""
    cleaned_key = _clean_key(key).encode('ascii')
    k_len = len(cleaned_key)
    return bytes((b + cleaned_key[i % k_len]) % 256 for i, b in enumerate(data))


def vigenere_bytes_decrypt(data: bytes, key: str) -> bytes:
    """Dekripsi byte-level Modulo-256 Vigenère Cipher untuk file biner."""
    cleaned_key = _clean_key(key).encode('ascii')
    k_len = len(cleaned_key)
    return bytes((b - cleaned_key[i % k_len]) % 256 for i, b in enumerate(data))


def rsa_hybrid_encrypt_bytes(data: bytes, public_key_pem: str, force_direct_chunking: bool = False) -> Tuple[bytes, str]:
    """
    Enkripsi file biner dengan RSA.
    - Jika data <= 4096 bytes atau force_direct_chunking=True: gunakan rsa_encrypt (chunking langsung).
    - Jika data > 4096 bytes: gunakan Standar Industri Hybrid Digital Envelope (RSA-OAEP mengenkripsi
      Session Key 32-byte acak, dan RC4 stream cipher mengenkripsi payload file besar dengan instan).
    Format Paket Hybrid: b"EDHY" + struct.pack(">H", len(enc_session_key)) + enc_session_key + enc_payload
    """
    if force_direct_chunking or len(data) <= 4096:
        return rsa_encrypt(data, public_key_pem), "RSA-OAEP Direct Block Chunking"

    session_key = get_random_bytes(32)
    enc_session_key = rsa_encrypt(session_key, public_key_pem)
    enc_payload = rc4_crypt(data, session_key)
    header = b"EDHY" + struct.pack(">H", len(enc_session_key))
    return header + enc_session_key + enc_payload, "RSA-OAEP Hybrid Digital Envelope (256-bit Session Key)"


def rsa_hybrid_decrypt_bytes(ciphertext: bytes, private_key_pem: str) -> Tuple[bytes, str]:
    """
    Dekripsi file biner yang dienkripsi dengan rsa_hybrid_encrypt_bytes atau rsa_encrypt.
    Mendeteksi secara otomatis apakah menggunakan Hybrid Envelope (header b"EDHY") atau Direct Chunking.
    """
    if ciphertext.startswith(b"EDHY") and len(ciphertext) >= 6:
        key_len = struct.unpack(">H", ciphertext[4:6])[0]
        if len(ciphertext) >= 6 + key_len:
            enc_session_key = ciphertext[6:6 + key_len]
            enc_payload = ciphertext[6 + key_len:]
            session_key = rsa_decrypt(enc_session_key, private_key_pem)
            decrypted_data = rc4_crypt(enc_payload, session_key)
            return decrypted_data, "RSA-OAEP Hybrid Digital Envelope"

    return rsa_decrypt(ciphertext, private_key_pem), "RSA-OAEP Direct Block Chunking"


def encrypt_file_container(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    algorithm: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mengenkripsi file apa pun (Gambar, Audio, Video, PDF, Dokumen, Biner) menggunakan algoritma pilihan
    dan membungkusnya dalam format kontainer terautentikasi (.ecry) beserta checksum SHA-256.
    Algoritma: 'caesar', 'vigenere', 'rc4', 'rsa', 'super'
    """
    t0 = time.perf_counter()
    orig_sha256 = hashlib.sha256(file_bytes).hexdigest()
    mode_detail = ""

    if algorithm == "caesar":
        shift = int(params.get("shift", 3))
        payload_cipher = caesar_bytes_encrypt(file_bytes, shift)
        mode_detail = f"Modulo-256 Byte Caesar (Shift +{shift})"

    elif algorithm == "vigenere":
        key = str(params.get("key", "GARUDA"))
        payload_cipher = vigenere_bytes_encrypt(file_bytes, key)
        mode_detail = f"Modulo-256 Poly-Byte Vigenère (Key len: {len(_clean_key(key))})"

    elif algorithm == "rc4":
        key = str(params.get("key", "")).encode('utf-8')
        payload_cipher = rc4_crypt(file_bytes, key)
        mode_detail = "RC4 Symmetric Keystream XOR"

    elif algorithm == "rsa":
        pub_pem = str(params.get("public_key", ""))
        payload_cipher, mode_detail = rsa_hybrid_encrypt_bytes(file_bytes, pub_pem)

    elif algorithm == "super":
        shift = int(params.get("shift", 7))
        vig_key = str(params.get("vigenere_key", "NUSANTARA"))
        rc4_key = str(params.get("rc4_key", "")).encode('utf-8')
        pub_pem = str(params.get("public_key", ""))

        s1 = caesar_bytes_encrypt(file_bytes, shift)
        s2 = vigenere_bytes_encrypt(s1, vig_key)
        s3 = rc4_crypt(s2, rc4_key)
        payload_cipher, rsa_mode = rsa_hybrid_encrypt_bytes(s3, pub_pem)
        mode_detail = f"4-Layer Super Pipeline (Caesar -> Vigenère -> RC4 -> {rsa_mode})"
    else:
        raise ValueError(f"Algoritma tidak dikenali: {algorithm}")

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    cipher_sha256 = hashlib.sha256(payload_cipher).hexdigest()

    metadata = {
        "magic": "EDUCRYPTO_V2",
        "filename": filename,
        "mime_type": mime_type or "application/octet-stream",
        "algorithm": algorithm,
        "mode_detail": mode_detail,
        "orig_size": len(file_bytes),
        "cipher_size": len(payload_cipher),
        "orig_sha256": orig_sha256,
        "cipher_sha256": cipher_sha256,
        "timestamp": int(time.time())
    }
    meta_json = json.dumps(metadata).encode('utf-8')
    container_bytes = b"ECRY2" + struct.pack(">I", len(meta_json)) + meta_json + payload_cipher

    return {
        "container_bytes": container_bytes,
        "raw_cipher_bytes": payload_cipher,
        "metadata": metadata,
        "elapsed_ms": round(elapsed_ms, 2),
        "entropy_plain": calculate_shannon_entropy(file_bytes),
        "entropy_cipher": calculate_shannon_entropy(payload_cipher)
    }


def decrypt_file_container(
    input_bytes: bytes,
    algorithm: str,
    params: Dict[str, Any],
    fallback_filename: str = "decrypted_output.bin",
    fallback_mime: str = "application/octet-stream"
) -> Dict[str, Any]:
    """
    Mendekripsi file kontainer (.ecry) maupun file raw terenkripsi dan memverifikasi integritas SHA-256.
    """
    t0 = time.perf_counter()
    metadata = None
    payload_cipher = input_bytes

    if input_bytes.startswith(b"ECRY2") and len(input_bytes) > 9:
        meta_len = struct.unpack(">I", input_bytes[5:9])[0]
        if len(input_bytes) >= 9 + meta_len:
            try:
                metadata = json.loads(input_bytes[9:9 + meta_len].decode('utf-8'))
                payload_cipher = input_bytes[9 + meta_len:]
                algorithm = metadata.get("algorithm", algorithm)
            except Exception:
                metadata = None

    if algorithm == "caesar":
        shift = int(params.get("shift", 3))
        recovered_bytes = caesar_bytes_decrypt(payload_cipher, shift)

    elif algorithm == "vigenere":
        key = str(params.get("key", "GARUDA"))
        recovered_bytes = vigenere_bytes_decrypt(payload_cipher, key)

    elif algorithm == "rc4":
        key = str(params.get("key", "")).encode('utf-8')
        recovered_bytes = rc4_crypt(payload_cipher, key)

    elif algorithm == "rsa":
        priv_pem = str(params.get("private_key", ""))
        recovered_bytes, _ = rsa_hybrid_decrypt_bytes(payload_cipher, priv_pem)

    elif algorithm == "super":
        shift = int(params.get("shift", 7))
        vig_key = str(params.get("vigenere_key", "NUSANTARA"))
        rc4_key = str(params.get("rc4_key", "")).encode('utf-8')
        priv_pem = str(params.get("private_key", ""))

        s3, _ = rsa_hybrid_decrypt_bytes(payload_cipher, priv_pem)
        s2 = rc4_crypt(s3, rc4_key)
        s1 = vigenere_bytes_decrypt(s2, vig_key)
        recovered_bytes = caesar_bytes_decrypt(s1, shift)
    else:
        raise ValueError(f"Algoritma tidak dikenali: {algorithm}")

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    recovered_sha256 = hashlib.sha256(recovered_bytes).hexdigest()

    integrity_verified = None
    if metadata and "orig_sha256" in metadata:
        integrity_verified = (recovered_sha256 == metadata["orig_sha256"])
        if not integrity_verified:
            raise ValueError(
                "Kunci dekripsi salah atau file rusak! Checksum SHA-256 tidak cocok dengan file asli."
            )

    return {
        "recovered_bytes": recovered_bytes,
        "filename": metadata.get("filename", fallback_filename) if metadata else fallback_filename,
        "mime_type": metadata.get("mime_type", fallback_mime) if metadata else fallback_mime,
        "algorithm": algorithm,
        "metadata": metadata,
        "recovered_sha256": recovered_sha256,
        "integrity_verified": integrity_verified,
        "elapsed_ms": round(elapsed_ms, 2)
    }


# ==============================================================================
# 7. ANALISIS KRIPTOGRAFI, ENTROPI SHANNON, AVALANCHE EFFECT & KRIPTANALISIS
# ==============================================================================
def calculate_shannon_entropy(data: bytes) -> float:
    """
    Menghitung Entropi Informasi Shannon H(X) dalam satuan bits per byte (rentang 0.0000 - 8.0000).
    Semakin mendekati 8.0, semakin acak distribusi byte ciphertext (tahan analisis statistik).
    """
    if not data:
        return 0.0
    length = len(data)
    counts = Counter(data)
    entropy = -sum((count / length) * math.log2(count / length) for count in counts.values())
    return round(entropy, 4)


def calculate_index_of_coincidence(text: str) -> float:
    """
    Menghitung Index of Coincidence (IoC) untuk mengukur kerentanan terhadap analisis frekuensi.
    Bahasa alami (Indonesia/Inggris) ~ 0.065 - 0.075, sedangkan distribusi rata polialfabetik ~ 0.0385.
    """
    letters = [c.upper() for c in text if 'A' <= c.upper() <= 'Z']
    n = len(letters)
    if n <= 1:
        return 0.0
    counts = Counter(letters)
    numerator = sum(f * (f - 1) for f in counts.values())
    return round(numerator / (n * (n - 1)), 5)


def analyze_letter_frequency(text: str) -> Dict[str, Any]:
    """Menghitung distribusi frekuensi huruf A-Z (persentase & jumlah)."""
    letters = [c.upper() for c in text if 'A' <= c.upper() <= 'Z']
    total = len(letters)
    counts = Counter(letters)
    freq_list = []
    for code in range(ord('A'), ord('Z') + 1):
        ch = chr(code)
        cnt = counts.get(ch, 0)
        pct = round((cnt / total) * 100.0, 2) if total > 0 else 0.0
        freq_list.append({"letter": ch, "count": cnt, "percentage": pct})
    return {
        "total_alpha": total,
        "total_chars": len(text),
        "ioc": calculate_index_of_coincidence(text),
        "frequencies": freq_list
    }


def calculate_avalanche_effect(bytes_a: bytes, bytes_b: bytes) -> Dict[str, Any]:
    """
    Menghitung Avalanche Effect (persentase bit yang berubah / Hamming Distance)
    antara dua output ciphertext ketika input plaintext/key diubah 1 karakter/bit.
    """
    min_len = min(len(bytes_a), len(bytes_b))
    max_len = max(len(bytes_a), len(bytes_b))
    if max_len == 0:
        return {"bit_diff": 0, "total_bits": 0, "percentage": 0.0}

    diff_bits = 0
    for i in range(min_len):
        xor_val = bytes_a[i] ^ bytes_b[i]
        diff_bits += bin(xor_val).count('1')

    # Sisa byte jika panjang berbeda dihitung sebagai perubahan bit
    diff_bits += (max_len - min_len) * 8
    total_bits = max_len * 8
    pct = round((diff_bits / total_bits) * 100.0, 2)

    return {
        "bit_diff": diff_bits,
        "total_bits": total_bits,
        "percentage": pct,
        "byte_len_a": len(bytes_a),
        "byte_len_b": len(bytes_b)
    }


def caesar_brute_force_attack(ciphertext: str) -> List[Dict[str, Any]]:
    """
    Menjalankan simulasi serangan Exhaustive Key Search (Brute-Force) pada Caesar Cipher
    untuk seluruh 25 kemungkinan kunci beserta skor heuristik kata umum Bahasa Indonesia & Inggris.
    """
    common_clues = [
        "DAN", "YANG", "DI", "KE", "DARI", "INI", "ITU", "UNTUK", "DENGAN", "ADALAH",
        "RAHASIA", "DATA", "NEGARA", "KRIPTOGRAFI", "SERANG", "MUSUH", "OPERASI", "THE", "AND", "IS"
    ]
    candidates = []
    for s in range(1, 26):
        dec = decrypt_caesar(ciphertext, s)
        upper_words = [w.strip(".,!?:;\"'()[]{}") for w in dec.upper().split()]
        score = sum(25 for w in upper_words if w in common_clues)
        # Tambah bobot proporsi vokal wajar (30% - 50%)
        alpha_only = [c for c in dec.upper() if 'A' <= c <= 'Z']
        if alpha_only:
            vowel_ratio = sum(1 for c in alpha_only if c in "AIUEO") / len(alpha_only)
            if 0.30 <= vowel_ratio <= 0.52:
                score += 15
        candidates.append({
            "shift": s,
            "plaintext": dec,
            "confidence_score": min(score, 100)
        })
    candidates.sort(key=lambda x: x["confidence_score"], reverse=True)
    return candidates


def inspect_rc4_state(key_str: str, sample_len: int = 16) -> Dict[str, Any]:
    """
    Mengembalikan matriks permutasi S-Box 256-byte hasil KSA dan sampel byte keystream PRGA
    untuk keperluan visualisasi akademik di depan dosen.
    """
    key_bytes = key_str.encode('utf-8')
    if not key_bytes:
        raise ValueError("Kunci RC4 tidak boleh kosong.")
    s_box = rc4_ksa(key_bytes)
    s_copy = list(s_box)
    prga_gen = rc4_prga(s_copy)
    keystream_sample = [next(prga_gen) for _ in range(sample_len)]
    return {
        "s_box": s_box,
        "keystream_dec": keystream_sample,
        "keystream_hex": [f"{b:02X}" for b in keystream_sample]
    }


def inspect_rsa_key_details(pem_str: str) -> Dict[str, Any]:
    """Mengekstrak parameter matematis kunci RSA (Modulus n, Public Exponent e, Bit size, Key type)."""
    rsa_key = RSA.import_key(pem_str)
    n_hex = hex(rsa_key.n)[2:].upper()
    return {
        "bits": rsa_key.size_in_bits(),
        "bytes": rsa_key.size_in_bytes(),
        "max_oaep_chunk_bytes": rsa_key.size_in_bytes() - 42,
        "has_private": rsa_key.has_private(),
        "e": str(rsa_key.e),
        "n_digits": len(str(rsa_key.n)),
        "n_preview": f"{n_hex[:32]}...{n_hex[-32:]}" if len(n_hex) > 64 else n_hex
    }
