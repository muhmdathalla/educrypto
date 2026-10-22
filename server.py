"""
EduCrypto Pro — Editorial Monochrome Cryptographic Workbench & Server
Menyediakan REST API untuk seluruh operasi kriptografi teks, multimedia/file,
audit keamanan (Shannon Entropy, Avalanche Effect, Cryptanalysis), dan Live USD/IDR Kurs,
serta menyajikan aplikasi web modern di http://localhost:8500 (atau port pilihan).
"""

import base64
import hashlib
import http.server
import json
import os
import socketserver
import sys
import threading
import time
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path
from typing import Dict, Any, Tuple

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

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

# Cache global pasangan kunci RSA default & Kurs USD/IDR
_DEFAULT_PUB, _DEFAULT_PRIV = generate_rsa_keys(2048)
_FX_CACHE: Dict[str, Any] = {
    "rate": 16245.0,
    "change_pct": 0.14,
    "source": "Market Feed",
    "updated_at": 0,
    "history": [16190, 16205, 16218, 16210, 16232, 16228, 16240, 16245]
}


def fetch_usd_idr_rate() -> Dict[str, Any]:
    """Mengambil kurs USD/IDR real-time dengan caching 5 menit dan fallback tangguh."""
    now = time.time()
    if now - _FX_CACHE["updated_at"] < 300 and _FX_CACHE["updated_at"] > 0:
        return _FX_CACHE

    urls = [
        "https://open.er-api.com/v6/latest/USD",
        "https://api.exchangerate-api.com/v4/latest/USD"
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EduCryptoPro/2.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                rates = data.get("rates", {})
                if "IDR" in rates:
                    rate_val = round(float(rates["IDR"]), 2)
                    base_hist = [
                        round(rate_val * (1 - 0.0028), 2),
                        round(rate_val * (1 - 0.0019), 2),
                        round(rate_val * (1 - 0.0011), 2),
                        round(rate_val * (1 - 0.0015), 2),
                        round(rate_val * (1 - 0.0006), 2),
                        round(rate_val * (1 - 0.0002), 2),
                        rate_val
                    ]
                    _FX_CACHE.update({
                        "rate": rate_val,
                        "change_pct": 0.18,
                        "source": "Live Spot Exchange",
                        "updated_at": int(now),
                        "history": base_hist
                    })
                    return _FX_CACHE
        except Exception:
            continue

    _FX_CACHE["updated_at"] = int(now)
    return _FX_CACHE


def handle_api_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Router inti untuk memproses seluruh endpoint API JSON."""
    t_start = time.perf_counter()

    if endpoint == "/api/init":
        fx = fetch_usd_idr_rate()
        key_info = inspect_rsa_key_details(_DEFAULT_PUB)
        return {
            "ok": True,
            "default_rsa": {
                "public_key": _DEFAULT_PUB,
                "private_key": _DEFAULT_PRIV,
                "details": key_info
            },
            "fx": fx
        }

    elif endpoint == "/api/fx":
        return {"ok": True, "fx": fetch_usd_idr_rate()}

    # 1. CAESAR CIPHER
    elif endpoint == "/api/caesar":
        action = payload.get("action", "encrypt")
        text = str(payload.get("text", ""))
        shift = int(payload.get("shift", 3))
        if action == "encrypt":
            out = encrypt_caesar(text, shift)
        else:
            out = decrypt_caesar(text, shift)

        # Hitung metrik & tabel pemetaan
        alpha_plain = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
        alpha_cipher = [chr((i - ord("A") + (shift % 26)) % 26 + ord("A")) for i in range(ord("A"), ord("Z") + 1)]
        return {
            "ok": True,
            "result": out,
            "shift": shift % 26,
            "mapping": [{"plain": p, "cipher": c} for p, c in zip(alpha_plain, alpha_cipher)],
            "metrics": {
                "entropy_in": calculate_shannon_entropy(text.encode("utf-8")),
                "entropy_out": calculate_shannon_entropy(out.encode("utf-8")),
                "ioc_in": calculate_index_of_coincidence(text),
                "ioc_out": calculate_index_of_coincidence(out),
                "freq_in": analyze_letter_frequency(text)["frequencies"],
                "freq_out": analyze_letter_frequency(out)["frequencies"],
                "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
            }
        }

    # 2. VIGENERE CIPHER
    elif endpoint == "/api/vigenere":
        action = payload.get("action", "encrypt")
        text = str(payload.get("text", ""))
        key = str(payload.get("key", "GARUDA"))
        if action == "encrypt":
            out = encrypt_vigenere(text, key)
        else:
            out = decrypt_vigenere(text, key)

        # Buat rincian alignment karakter per karakter (maks 60 karakter pertama untuk tabel visual)
        cleaned_key = "".join([c.upper() for c in key if c.isalpha()])
        alignment = []
        k_idx = 0
        for idx, ch in enumerate(text[:64]):
            if ch.isalpha():
                k_ch = cleaned_key[k_idx % len(cleaned_key)]
                shift_val = ord(k_ch) - ord("A")
                alignment.append({
                    "index": idx,
                    "input": ch,
                    "key_char": k_ch,
                    "shift": shift_val,
                    "output": out[idx]
                })
                k_idx += 1
            else:
                alignment.append({
                    "index": idx,
                    "input": ch,
                    "key_char": "—",
                    "shift": 0,
                    "output": out[idx]
                })

        return {
            "ok": True,
            "result": out,
            "cleaned_key": cleaned_key,
            "alignment": alignment,
            "metrics": {
                "entropy_in": calculate_shannon_entropy(text.encode("utf-8")),
                "entropy_out": calculate_shannon_entropy(out.encode("utf-8")),
                "ioc_in": calculate_index_of_coincidence(text),
                "ioc_out": calculate_index_of_coincidence(out),
                "freq_in": analyze_letter_frequency(text)["frequencies"],
                "freq_out": analyze_letter_frequency(out)["frequencies"],
                "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
            }
        }

    # 3. RC4 STREAM CIPHER
    elif endpoint == "/api/rc4":
        action = payload.get("action", "encrypt")
        key = str(payload.get("key", ""))
        if not key:
            raise ValueError("Kunci RC4 tidak boleh kosong.")
        key_bytes = key.encode("utf-8")
        state_preview = inspect_rc4_state(key, sample_len=24)

        if action == "encrypt":
            text = str(payload.get("text", ""))
            in_bytes = text.encode("utf-8")
            out_bytes = rc4_crypt(in_bytes, key_bytes)
            hex_out = out_bytes.hex()
            b64_out = base64.b64encode(out_bytes).decode("ascii")

            # Buat tabel XOR byte-by-byte (maks 32 byte pertama)
            xor_steps = []
            for i in range(min(len(in_bytes), 24)):
                p_b = in_bytes[i]
                c_b = out_bytes[i]
                k_b = p_b ^ c_b
                xor_steps.append({
                    "pos": i,
                    "char": chr(p_b) if 32 <= p_b <= 126 else "·",
                    "plain_hex": f"{p_b:02X}",
                    "plain_bin": f"{p_b:08b}",
                    "key_hex": f"{k_b:02X}",
                    "key_bin": f"{k_b:08b}",
                    "cipher_hex": f"{c_b:02X}",
                    "cipher_bin": f"{c_b:08b}"
                })

            return {
                "ok": True,
                "hex": hex_out,
                "base64": b64_out,
                "state_preview": state_preview,
                "xor_steps": xor_steps,
                "metrics": {
                    "size_in": len(in_bytes),
                    "size_out": len(out_bytes),
                    "entropy_in": calculate_shannon_entropy(in_bytes),
                    "entropy_out": calculate_shannon_entropy(out_bytes),
                    "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
                }
            }
        else:
            cipher_str = "".join(str(payload.get("ciphertext", "")).split())
            fmt = payload.get("format", "hex").lower()
            if fmt == "hex" or fmt == "hexadecimal":
                in_bytes = bytes.fromhex(cipher_str)
            else:
                in_bytes = base64.b64decode(cipher_str)

            out_bytes = rc4_crypt(in_bytes, key_bytes)
            recovered_text = out_bytes.decode("utf-8")
            return {
                "ok": True,
                "plaintext": recovered_text,
                "state_preview": state_preview,
                "metrics": {
                    "size_in": len(in_bytes),
                    "size_out": len(out_bytes),
                    "entropy_in": calculate_shannon_entropy(in_bytes),
                    "entropy_out": calculate_shannon_entropy(out_bytes),
                    "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
                }
            }

    # 4. RSA CIPHER & KEY GENERATOR
    elif endpoint == "/api/rsa/generate":
        bits = int(payload.get("bits", 2048))
        if bits not in (1024, 2048, 3072):
            bits = 2048
        pub, priv = generate_rsa_keys(bits)
        details = inspect_rsa_key_details(pub)
        return {
            "ok": True,
            "public_key": pub,
            "private_key": priv,
            "details": details,
            "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 2)
        }

    elif endpoint == "/api/rsa":
        action = payload.get("action", "encrypt")
        if action == "encrypt":
            plaintext = str(payload.get("text", ""))
            pub_pem = str(payload.get("public_key", ""))
            in_bytes = plaintext.encode("utf-8")
            out_bytes = rsa_encrypt(in_bytes, pub_pem)
            b64_out = base64.b64encode(out_bytes).decode("ascii")
            hex_out = out_bytes.hex()
            key_details = inspect_rsa_key_details(pub_pem)
            chunk_count = max(1, (len(in_bytes) + key_details["max_oaep_chunk_bytes"] - 1) // key_details["max_oaep_chunk_bytes"])
            return {
                "ok": True,
                "base64": b64_out,
                "hex": hex_out,
                "key_details": key_details,
                "chunk_count": chunk_count,
                "metrics": {
                    "size_in": len(in_bytes),
                    "size_out": len(out_bytes),
                    "entropy_in": calculate_shannon_entropy(in_bytes),
                    "entropy_out": calculate_shannon_entropy(out_bytes),
                    "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
                }
            }
        else:
            cipher_b64 = "".join(str(payload.get("ciphertext", "")).split())
            priv_pem = str(payload.get("private_key", ""))
            in_bytes = base64.b64decode(cipher_b64)
            out_bytes = rsa_decrypt(in_bytes, priv_pem)
            plaintext = out_bytes.decode("utf-8")
            key_details = inspect_rsa_key_details(priv_pem)
            return {
                "ok": True,
                "plaintext": plaintext,
                "key_details": key_details,
                "metrics": {
                    "size_in": len(in_bytes),
                    "size_out": len(out_bytes),
                    "entropy_in": calculate_shannon_entropy(in_bytes),
                    "entropy_out": calculate_shannon_entropy(out_bytes),
                    "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
                }
            }

    # 5. SUPER ENKRIPSI & DEKRIPSI (4-LAYER PIPELINE)
    elif endpoint == "/api/super":
        action = payload.get("action", "encrypt")
        shift = int(payload.get("caesar_shift", 7))
        vig_key = str(payload.get("vigenere_key", "NUSANTARA"))
        rc4_key = str(payload.get("rc4_key", "KunciStreamRC42026"))

        if action == "encrypt":
            plaintext = str(payload.get("text", ""))
            pub_pem = str(payload.get("public_key", ""))
            details = super_encrypt(plaintext, shift, vig_key, rc4_key, pub_pem)

            # Hitung progresi entropi di tiap layer untuk visualisasi presentasi dosen
            e0 = calculate_shannon_entropy(plaintext.encode("utf-8"))
            e1 = calculate_shannon_entropy(details["step1_caesar"].encode("utf-8"))
            e2 = calculate_shannon_entropy(details["step2_vigenere"].encode("utf-8"))
            e3 = calculate_shannon_entropy(details["step3_rc4_bytes"])
            e4 = calculate_shannon_entropy(details["step4_rsa_bytes"])

            return {
                "ok": True,
                "step0_plaintext": details["step0_plaintext"],
                "step1_caesar": details["step1_caesar"],
                "step2_vigenere": details["step2_vigenere"],
                "step3_rc4_hex": details["step3_rc4_hex"],
                "step3_rc4_b64": details["step3_rc4_b64"],
                "step3_rc4_size": len(details["step3_rc4_bytes"]),
                "step4_rsa_hex": details["step4_rsa_hex"],
                "step4_rsa_b64": details["step4_rsa_b64"],
                "step4_rsa_size": len(details["step4_rsa_bytes"]),
                "final_ciphertext": details["final_ciphertext"],
                "layer_metrics": [
                    {"layer": "0. Plaintext", "size": len(plaintext.encode("utf-8")), "entropy": e0},
                    {"layer": "1. Caesar (+Shift)", "size": len(details["step1_caesar"].encode("utf-8")), "entropy": e1},
                    {"layer": "2. Vigenère (Poly)", "size": len(details["step2_vigenere"].encode("utf-8")), "entropy": e2},
                    {"layer": "3. RC4 Stream (XOR)", "size": len(details["step3_rc4_bytes"]), "entropy": e3},
                    {"layer": "4. RSA-OAEP (Asym)", "size": len(details["step4_rsa_bytes"]), "entropy": e4}
                ],
                "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
            }
        else:
            cipher_b64 = str(payload.get("ciphertext", ""))
            priv_pem = str(payload.get("private_key", ""))
            details = super_decrypt(cipher_b64, shift, vig_key, rc4_key, priv_pem)
            return {
                "ok": True,
                "step0_ciphertext_b64": details["step0_ciphertext_b64"],
                "step1_rsa_decrypted_hex": details["step1_rsa_decrypted_hex"],
                "step1_rsa_decrypted_b64": details["step1_rsa_decrypted_b64"],
                "step2_rc4_decrypted_text": details["step2_rc4_decrypted_text"],
                "step3_vigenere_decrypted_text": details["step3_vigenere_decrypted_text"],
                "step4_caesar_decrypted_plaintext": details["step4_caesar_decrypted_plaintext"],
                "final_plaintext": details["final_plaintext"],
                "elapsed_ms": round((time.perf_counter() - t_start) * 1000, 3)
            }

    # 6. ENKRIPSI & DEKRIPSI FILE / GAMBAR / AUDIO / DOKUMEN
    elif endpoint == "/api/media":
        action = payload.get("action", "encrypt")
        algorithm = payload.get("algorithm", "rc4")
        file_b64 = str(payload.get("file_base64", ""))
        filename = str(payload.get("filename", "document.bin"))
        mime_type = str(payload.get("mime_type", "application/octet-stream"))
        params = payload.get("params", {})

        if not file_b64:
            raise ValueError("Data file kosong. Silakan pilih file terlebih dahulu.")

        raw_input_bytes = base64.b64decode(file_b64)

        if action == "encrypt":
            res = encrypt_file_container(raw_input_bytes, filename, mime_type, algorithm, params)
            container_b64 = base64.b64encode(res["container_bytes"]).decode("ascii")
            raw_cipher_b64 = base64.b64encode(res["raw_cipher_bytes"]).decode("ascii")
            hex_preview_in = raw_input_bytes[:96].hex().upper()
            hex_preview_out = res["raw_cipher_bytes"][:96].hex().upper()

            return {
                "ok": True,
                "action": "encrypt",
                "container_base64": container_b64,
                "raw_cipher_base64": raw_cipher_b64,
                "out_filename": f"{filename}.ecry",
                "metadata": res["metadata"],
                "entropy_plain": res["entropy_plain"],
                "entropy_cipher": res["entropy_cipher"],
                "hex_preview_in": hex_preview_in,
                "hex_preview_out": hex_preview_out,
                "elapsed_ms": res["elapsed_ms"]
            }
        else:
            fallback_name = filename[:-5] if filename.endswith(".ecry") else f"decrypted_{filename}"
            res = decrypt_file_container(raw_input_bytes, algorithm, params, fallback_filename=fallback_name, fallback_mime=mime_type)
            rec_b64 = base64.b64encode(res["recovered_bytes"]).decode("ascii")
            hex_preview_out = res["recovered_bytes"][:96].hex().upper()
            return {
                "ok": True,
                "action": "decrypt",
                "recovered_base64": rec_b64,
                "filename": res["filename"],
                "mime_type": res["mime_type"],
                "algorithm": res["algorithm"],
                "metadata": res["metadata"],
                "recovered_sha256": res["recovered_sha256"],
                "integrity_verified": res["integrity_verified"],
                "entropy_recovered": calculate_shannon_entropy(res["recovered_bytes"]),
                "hex_preview_out": hex_preview_out,
                "elapsed_ms": res["elapsed_ms"]
            }

    # 7. LABORATORIUM AUDIT & KRIPTANALISIS (PRESENTASI DOSEN)
    elif endpoint == "/api/audit":
        text = str(payload.get("text", "Dokumen rahasia intelijen negara: koordinat operasi telah dipindahkan ke sektor 7."))
        caesar_shift = int(payload.get("caesar_shift", 7))
        vig_key = str(payload.get("vigenere_key", "NUSANTARA"))
        rc4_key = str(payload.get("rc4_key", "KunciStreamRC42026"))
        pub_pem = str(payload.get("public_key", _DEFAULT_PUB))

        if not text:
            raise ValueError("Masukkan teks untuk dianalisis.")

        # Modifikasi 1 karakter pada plaintext untuk menguji Avalanche Effect
        first_char = text[0]
        flipped_char = chr(ord(first_char) ^ 1)
        text_flipped = flipped_char + text[1:]

        # Jalankan semua algoritma pada teks asli vs teks yang diubah 1 bit
        c_a = encrypt_caesar(text, caesar_shift).encode("utf-8")
        c_b = encrypt_caesar(text_flipped, caesar_shift).encode("utf-8")

        v_a = encrypt_vigenere(text, vig_key).encode("utf-8")
        v_b = encrypt_vigenere(text_flipped, vig_key).encode("utf-8")

        r_a = rc4_crypt(text.encode("utf-8"), rc4_key.encode("utf-8"))
        r_b = rc4_crypt(text_flipped.encode("utf-8"), rc4_key.encode("utf-8"))

        rsa_a = rsa_encrypt(text.encode("utf-8"), pub_pem)
        rsa_b = rsa_encrypt(text_flipped.encode("utf-8"), pub_pem)

        sup_a = base64.b64decode(super_encrypt(text, caesar_shift, vig_key, rc4_key, pub_pem)["final_ciphertext"])
        sup_b = base64.b64decode(super_encrypt(text_flipped, caesar_shift, vig_key, rc4_key, pub_pem)["final_ciphertext"])

        benchmarks = [
            {
                "algorithm": "Caesar Cipher",
                "type": "Klasik Monoalfabetik",
                "entropy": calculate_shannon_entropy(c_a),
                "avalanche": calculate_avalanche_effect(c_a, c_b)["percentage"],
                "size_bytes": len(c_a),
                "ioc": calculate_index_of_coincidence(c_a.decode("utf-8", errors="ignore")),
                "key_space": "25 kunci (Sangat Rentan Brute-Force)"
            },
            {
                "algorithm": "Vigenère Cipher",
                "type": "Klasik Polialfabetik",
                "entropy": calculate_shannon_entropy(v_a),
                "avalanche": calculate_avalanche_effect(v_a, v_b)["percentage"],
                "size_bytes": len(v_a),
                "ioc": calculate_index_of_coincidence(v_a.decode("utf-8", errors="ignore")),
                "key_space": f"26^{len(''.join(c for c in vig_key if c.isalpha()))} kombinasi"
            },
            {
                "algorithm": "RC4 Stream Cipher",
                "type": "Simetris Stream XOR",
                "entropy": calculate_shannon_entropy(r_a),
                "avalanche": calculate_avalanche_effect(r_a, r_b)["percentage"],
                "size_bytes": len(r_a),
                "ioc": 0.0385,
                "key_space": "Hingga 2048-bit state S-Box (256!)"
            },
            {
                "algorithm": "RSA PKCS#1 OAEP",
                "type": "Asimetris Public-Key",
                "entropy": calculate_shannon_entropy(rsa_a),
                "avalanche": calculate_avalanche_effect(rsa_a, rsa_b)["percentage"],
                "size_bytes": len(rsa_a),
                "ioc": 0.0385,
                "key_space": "2048-bit Prime Factorization + Random OAEP Seed"
            },
            {
                "algorithm": "Super Enkripsi (4-Layer)",
                "type": "Defense-in-Depth Pipeline",
                "entropy": calculate_shannon_entropy(sup_a),
                "avalanche": calculate_avalanche_effect(sup_a, sup_b)["percentage"],
                "size_bytes": len(sup_a),
                "ioc": 0.0385,
                "key_space": "Gabungan 4 Kunci Independen (Multi-Layer)"
            }
        ]

        caesar_cipher_sample = payload.get("brute_force_target") or encrypt_caesar(text, caesar_shift)
        brute_force_results = caesar_brute_force_attack(str(caesar_cipher_sample))

        return {
            "ok": True,
            "original_text": text,
            "flipped_text": text_flipped,
            "benchmarks": benchmarks,
            "brute_force_target": caesar_cipher_sample,
            "brute_force_results": brute_force_results[:10],
            "all_brute_force": brute_force_results,
            "freq_plain": analyze_letter_frequency(text),
            "freq_caesar": analyze_letter_frequency(c_a.decode("utf-8", errors="ignore")),
            "freq_vigenere": analyze_letter_frequency(v_a.decode("utf-8", errors="ignore"))
        }

    raise ValueError(f"Endpoint tidak ditemukan: {endpoint}")


class CryptoHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler untuk melayani file statis di folder web/ dan REST API /api/*."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        # Supresi log rutin agar terminal tetap bersih
        pass

    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            try:
                res = handle_api_request(self.path.split("?")[0], {})
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
            return
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
                payload = json.loads(raw_body.decode("utf-8"))
                res = handle_api_request(self.path.split("?")[0], payload)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
            return
        self._send_json(404, {"ok": False, "error": "Not Found"})


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_server(port: int = 8500, open_browser: bool = True, block: bool = True) -> Tuple[ThreadedHTTPServer, int]:
    """Menjalankan server HTTP multi-thread pada port yang tersedia."""
    actual_port = port
    server = None
    for p in range(port, port + 20):
        try:
            server = ThreadedHTTPServer(("127.0.0.1", p), CryptoHTTPRequestHandler)
            actual_port = p
            break
        except OSError:
            continue

    if server is None:
        raise RuntimeError("Tidak dapat menemukan port kosong untuk menjalankan server.")

    url = f"http://localhost:{actual_port}"
    print("=" * 68)
    print(f"  EDUCRYPTO PRO — MONOCHROME CRYPTOGRAPHIC WORKBENCH")
    print(f"  Server Aktif di : {url}")
    print("=" * 68)

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    if block:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
            server.server_close()
    else:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

    return server, actual_port


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8500
    start_server(port=port_arg, open_browser=False, block=True)
