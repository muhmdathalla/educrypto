/**
 * EduCrypto Core Engine — Client-Side Pure JS Implementation (Netlify Standalone Compatible)
 * Menyediakan seluruh fungsi kriptografi, file vault, entropi, dan avalanche effect
 * secara mandiri di browser tanpa ketergantungan server backend.
 */

const CryptoEngine = (() => {
  // 1. CAESAR CIPHER
  function encryptCaesar(text, shift) {
    shift = ((shift % 26) + 26) % 26;
    let res = '';
    for (let i = 0; i < text.length; i++) {
      const code = text.charCodeAt(i);
      if (code >= 97 && code <= 122) { // a-z
        res += String.fromCharCode(((code - 97 + shift) % 26) + 97);
      } else if (code >= 65 && code <= 90) { // A-Z
        res += String.fromCharCode(((code - 65 + shift) % 26) + 65);
      } else {
        res += text[i];
      }
    }
    return res;
  }

  function decryptCaesar(text, shift) {
    return encryptCaesar(text, -shift);
  }

  // 2. VIGENERE CIPHER
  function cleanVigKey(key) {
    const cleaned = (key || '').replace(/[^a-zA-Z]/g, '').toUpperCase();
    if (!cleaned) throw new Error('Kunci Vigenère harus mengandung minimal 1 huruf alfabet (A-Z).');
    return cleaned;
  }

  function encryptVigenere(text, key) {
    const k = cleanVigKey(key);
    let res = '';
    let kIdx = 0;
    for (let i = 0; i < text.length; i++) {
      const code = text.charCodeAt(i);
      if (code >= 97 && code <= 122) {
        const shift = k.charCodeAt(kIdx % k.length) - 65;
        res += String.fromCharCode(((code - 97 + shift) % 26) + 97);
        kIdx++;
      } else if (code >= 65 && code <= 90) {
        const shift = k.charCodeAt(kIdx % k.length) - 65;
        res += String.fromCharCode(((code - 65 + shift) % 26) + 65);
        kIdx++;
      } else {
        res += text[i];
      }
    }
    return res;
  }

  function decryptVigenere(text, key) {
    const k = cleanVigKey(key);
    let res = '';
    let kIdx = 0;
    for (let i = 0; i < text.length; i++) {
      const code = text.charCodeAt(i);
      if (code >= 97 && code <= 122) {
        const shift = k.charCodeAt(kIdx % k.length) - 65;
        res += String.fromCharCode(((code - 97 - shift + 26) % 26) + 97);
        kIdx++;
      } else if (code >= 65 && code <= 90) {
        const shift = k.charCodeAt(kIdx % k.length) - 65;
        res += String.fromCharCode(((code - 65 - shift + 26) % 26) + 65);
        kIdx++;
      } else {
        res += text[i];
      }
    }
    return res;
  }

  // 3. RC4 STREAM CIPHER (KSA & PRGA)
  function rc4Ksa(keyBytes) {
    const s = new Array(256);
    for (let i = 0; i < 256; i++) s[i] = i;
    let j = 0;
    const len = keyBytes.length;
    for (let i = 0; i < 256; i++) {
      j = (j + s[i] + keyBytes[i % len]) % 256;
      const tmp = s[i]; s[i] = s[j]; s[j] = tmp;
    }
    return s;
  }

  function rc4Crypt(dataBytes, keyBytes) {
    if (!keyBytes || keyBytes.length === 0) throw new Error('Kunci RC4 tidak boleh kosong.');
    const s = rc4Ksa(keyBytes);
    let i = 0, j = 0;
    const out = new Uint8Array(dataBytes.length);
    for (let idx = 0; idx < dataBytes.length; idx++) {
      i = (i + 1) % 256;
      j = (j + s[i]) % 256;
      const tmp = s[i]; s[i] = s[j]; s[j] = tmp;
      const k = s[(s[i] + s[j]) % 256];
      out[idx] = dataBytes[idx] ^ k;
    }
    return out;
  }

  // 4. ENTROPY, IoC & AVALANCHE
  function calculateEntropy(bytes) {
    if (!bytes || bytes.length === 0) return 0.0;
    const counts = {};
    for (let b of bytes) counts[b] = (counts[b] || 0) + 1;
    let entropy = 0.0;
    const len = bytes.length;
    for (let b in counts) {
      const p = counts[b] / len;
      entropy -= p * Math.log2(p);
    }
    return parseFloat(entropy.toFixed(4));
  }

  function calculateIoC(text) {
    const letters = (text || '').toUpperCase().replace(/[^A-Z]/g, '');
    const n = letters.length;
    if (n <= 1) return 0.0;
    const counts = {};
    for (let ch of letters) counts[ch] = (counts[ch] || 0) + 1;
    let numerator = 0;
    for (let ch in counts) numerator += counts[ch] * (counts[ch] - 1);
    return parseFloat((numerator / (n * (n - 1))).toFixed(5));
  }

  function calculateAvalanche(bytesA, bytesB) {
    const minLen = Math.min(bytesA.length, bytesB.length);
    const maxLen = Math.max(bytesA.length, bytesB.length);
    if (maxLen === 0) return { percentage: 0.0, bitDiff: 0 };
    let bitDiff = 0;
    for (let i = 0; i < minLen; i++) {
      let xor = bytesA[i] ^ bytesB[i];
      while (xor > 0) {
        if (xor & 1) bitDiff++;
        xor >>= 1;
      }
    }
    bitDiff += (maxLen - minLen) * 8;
    const totalBits = maxLen * 8;
    return {
      percentage: parseFloat(((bitDiff / totalBits) * 100).toFixed(2)),
      bitDiff,
      totalBits
    };
  }

  function analyzeFrequencies(text) {
    const letters = (text || '').toUpperCase().replace(/[^A-Z]/g, '');
    const total = letters.length;
    const counts = {};
    for (let ch of letters) counts[ch] = (counts[ch] || 0) + 1;
    const frequencies = [];
    for (let i = 65; i <= 90; i++) {
      const ch = String.fromCharCode(i);
      const cnt = counts[ch] || 0;
      frequencies.push({
        letter: ch,
        count: cnt,
        percentage: total > 0 ? parseFloat(((cnt / total) * 100).toFixed(2)) : 0.0
      });
    }
    return { total, frequencies, ioc: calculateIoC(text) };
  }

  function bruteForceCaesar(ciphertext) {
    const clues = ['DAN', 'YANG', 'DI', 'KE', 'DARI', 'INI', 'ITU', 'UNTUK', 'DENGAN', 'ADALAH', 'RAHASIA', 'DATA', 'NEGARA', 'KRIPTOGRAFI', 'SERANG', 'MUSUH', 'OPERASI', 'THE', 'AND', 'IS'];
    const candidates = [];
    for (let s = 1; s <= 25; s++) {
      const dec = decryptCaesar(ciphertext, s);
      const words = dec.toUpperCase().replace(/[.,!?:;"'()[\]{}]/g, '').split(/\s+/);
      let score = 0;
      for (let w of words) {
        if (clues.includes(w)) score += 25;
      }
      const alphaOnly = dec.toUpperCase().replace(/[^A-Z]/g, '');
      if (alphaOnly.length > 0) {
        let vowels = 0;
        for (let c of alphaOnly) if ('AIUEO'.includes(c)) vowels++;
        const ratio = vowels / alphaOnly.length;
        if (ratio >= 0.30 && ratio <= 0.52) score += 15;
      }
      candidates.push({
        shift: s,
        plaintext: dec,
        confidence_score: Math.min(score, 100)
      });
    }
    candidates.sort((a, b) => b.confidence_score - a.confidence_score);
    return candidates;
  }

  // 5. FILE CONTAINER PROTOCOL (.ecry)
  function caesarBytes(bytes, shift) {
    shift = ((shift % 256) + 256) % 256;
    const out = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) out[i] = (bytes[i] + shift) % 256;
    return out;
  }

  function vigenereBytes(bytes, keyStr) {
    const cleaned = cleanVigKey(keyStr);
    const kBytes = new TextEncoder().encode(cleaned);
    const out = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) {
      out[i] = (bytes[i] + kBytes[i % kBytes.length]) % 256;
    }
    return out;
  }

  function vigenereBytesDec(bytes, keyStr) {
    const cleaned = cleanVigKey(keyStr);
    const kBytes = new TextEncoder().encode(cleaned);
    const out = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) {
      out[i] = (bytes[i] - kBytes[i % kBytes.length] + 256) % 256;
    }
    return out;
  }

  async function sha256Hex(bytes) {
    if (typeof window !== 'undefined' && window.crypto && window.crypto.subtle) {
      try {
        const hashBuffer = await window.crypto.subtle.digest('SHA-256', bytes);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      } catch (e) {}
    }
    function rightRotate(value, amount) {
      return (value >>> amount) | (value << (32 - amount));
    }
    let result = '';
    const words = [];
    const asciiBitLength = bytes.length * 8;
    const hash = [
      0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ];
    const k = [
      0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ];
    for (let i = 0; i < bytes.length; i++) {
      words[i >> 2] |= bytes[i] << ((3 - (i % 4)) * 8);
    }
    words[bytes.length >> 2] |= 0x80 << ((3 - (bytes.length % 4)) * 8);
    words[(((bytes.length + 8) >> 6) + 1) * 16 - 1] = asciiBitLength;
    const w = new Array(64);
    for (let i = 0; i < words.length; i += 16) {
      let a = hash[0], b = hash[1], c = hash[2], d = hash[3], e = hash[4], f = hash[5], g = hash[6], h = hash[7];
      for (let j = 0; j < 64; j++) {
        if (j < 16) {
          w[j] = words[i + j] | 0;
        } else {
          const s0 = rightRotate(w[j - 15], 7) ^ rightRotate(w[j - 15], 18) ^ (w[j - 15] >>> 3);
          const s1 = rightRotate(w[j - 2], 17) ^ rightRotate(w[j - 2], 19) ^ (w[j - 2] >>> 10);
          w[j] = (w[j - 16] + s0 + w[j - 7] + s1) | 0;
        }
        const s1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25);
        const ch = (e & f) ^ ((~e) & g);
        const temp1 = (h + s1 + ch + k[j] + w[j]) | 0;
        const s0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22);
        const maj = (a & b) ^ (a & c) ^ (b & c);
        const temp2 = (s0 + maj) | 0;
        h = g; g = f; f = e; e = (d + temp1) | 0; d = c; c = b; b = a; a = (temp1 + temp2) | 0;
      }
      hash[0] = (hash[0] + a) | 0; hash[1] = (hash[1] + b) | 0; hash[2] = (hash[2] + c) | 0; hash[3] = (hash[3] + d) | 0;
      hash[4] = (hash[4] + e) | 0; hash[5] = (hash[5] + f) | 0; hash[6] = (hash[6] + g) | 0; hash[7] = (hash[7] + h) | 0;
    }
    for (let i = 0; i < 8; i++) {
      result += (hash[i] >>> 0).toString(16).padStart(8, '0');
    }
    return result;
  }

  return {
    encryptCaesar,
    decryptCaesar,
    encryptVigenere,
    decryptVigenere,
    rc4Crypt,
    calculateEntropy,
    calculateIoC,
    calculateAvalanche,
    analyzeFrequencies,
    bruteForceCaesar,
    caesarBytes,
    vigenereBytes,
    vigenereBytesDec,
    sha256Hex
  };
})();
