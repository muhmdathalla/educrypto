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
    const hashBuffer = await crypto.subtle.digest('SHA-256', bytes);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
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
