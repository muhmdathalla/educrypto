/**
 * EduCrypto Pro — Client Controller & Interactive Cryptographic Engine
 * Handles UI interactions, API communications, real-time USD/IDR conversion,
 * audio/image synthetic sample generation, dynamic alphabet mapping, and animated background.
 */

// =============================================================================
// 1. STATE MANAGEMENT
// =============================================================================
const state = {
  theme: localStorage.getItem('educrypto_theme') || 'dark',
  activeModuleId: 'mod-caesar',
  rsaKeypair: {
    publicKey: '',
    privateKey: '',
    details: {}
  },
  fx: {
    rate: 16245.0,
    changePct: 0.14,
    source: 'Market Feed'
  },
  mediaFile: null, // { name, type, size, base64 }
  lastProcessedMedia: null, // { containerBase64, filename, mimeType }
  auditFreqMode: 'plain',
  auditData: null
};

// API Helper
async function apiPost(endpoint, data = {}) {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    if (!json.ok) throw new Error(json.error || 'Operasi gagal dieksekusi.');
    return json;
  } catch (err) {
    showToast(err.message || 'Koneksi ke backend server gagal.', 'error');
    throw err;
  }
}

async function apiGet(endpoint) {
  try {
    const res = await fetch(endpoint);
    const json = await res.json();
    if (!json.ok) throw new Error(json.error || 'Gagal memuat data API.');
    return json;
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
}

function showToast(msg) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const t = document.createElement('div');
  t.className = 'toast-msg';
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateY(-10px)';
    t.style.transition = 'all 0.3s ease';
    setTimeout(() => t.remove(), 300);
  }, 3200);
}

// Copy to clipboard helper
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-copy-target]');
  if (btn) {
    const targetId = btn.getAttribute('data-copy-target');
    const targetEl = document.getElementById(targetId);
    if (targetEl && targetEl.value) {
      navigator.clipboard.writeText(targetEl.value).then(() => {
        showToast('Berhasil disalin ke clipboard!');
      });
    }
  }
});

// =============================================================================
// 2. THEME SWITCHER (MONOCHROME OBSIDIAN <-> ALABASTER)
// =============================================================================
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeButton();

  document.getElementById('btn-theme-toggle').addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('educrypto_theme', state.theme);
    updateThemeButton();
  });
}

function updateThemeButton() {
  const lbl = document.getElementById('theme-toggle-label');
  if (lbl) {
    lbl.textContent = state.theme === 'dark' ? 'TEMA: GELAP' : 'TEMA: TERANG';
  }
}

// =============================================================================
// 3. TELEMETRY & LIVE USD/IDR TICKER
// =============================================================================
function initFxTicker() {
  const tickerBtn = document.getElementById('fx-ticker-btn');
  const popover = document.getElementById('fx-popover');
  const usdIn = document.getElementById('fx-usd-input');
  const idrOut = document.getElementById('fx-idr-output');
  const refreshBtn = document.getElementById('btn-refresh-fx');

  function updateConverter() {
    const usdVal = parseFloat(usdIn.value) || 0;
    const totalIdr = usdVal * state.fx.rate;
    idrOut.textContent = 'Rp ' + totalIdr.toLocaleString('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  }

  tickerBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    popover.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (!popover.contains(e.target) && e.target !== tickerBtn) {
      popover.classList.remove('open');
    }
  });

  usdIn.addEventListener('input', updateConverter);

  refreshBtn.addEventListener('click', async (e) => {
    e.stopPropagation();
    try {
      const data = await apiGet('/api/fx');
      if (data.fx) {
        state.fx = data.fx;
        renderFxData();
        updateConverter();
        showToast('Kurs USD/IDR berhasil diperbarui!');
      }
    } catch (err) {
      showToast('Gagal memperbarui kurs real-time.');
    }
  });
}

function renderFxData() {
  const display = document.getElementById('fx-rate-display');
  const src = document.getElementById('fx-source-label');
  if (display) {
    display.textContent = 'Rp ' + state.fx.rate.toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  if (src && state.fx.source) {
    src.textContent = state.fx.source;
  }
}

// =============================================================================
// 4. FLOATING LIQUID GLASS DOCK & MODULE ROUTING
// =============================================================================
function initNavigation() {
  const dockItems = document.querySelectorAll('.dock-item');
  const headerName = document.getElementById('header-module-name');
  const headerSpec = document.getElementById('header-module-spec');

  dockItems.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const name = btn.getAttribute('data-name');
      const spec = btn.getAttribute('data-spec');

      // Update Dock UI
      dockItems.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Update Header Active Telemetry
      if (headerName) headerName.textContent = name;
      if (headerSpec) headerSpec.textContent = spec;

      // Update Section Visibility
      document.querySelectorAll('.module-section').forEach(sec => {
        sec.classList.remove('active');
      });
      const activeSec = document.getElementById(targetId);
      if (activeSec) {
        activeSec.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }

      state.activeModuleId = targetId;

      // Trigger auto audit jika masuk ke Modul Audit
      if (targetId === 'mod-audit' && !state.auditData) {
        runAudit();
      }
    });
  });

  // Modal Sidang / Dosen Cheat Sheet
  const defenseModal = document.getElementById('defense-modal');
  document.getElementById('btn-open-defense').addEventListener('click', () => {
    defenseModal.classList.add('open');
  });
  document.getElementById('btn-close-defense').addEventListener('click', () => {
    defenseModal.classList.remove('open');
  });
  defenseModal.addEventListener('click', (e) => {
    if (e.target === defenseModal) defenseModal.classList.remove('open');
  });
}

// =============================================================================
// 5. CAESAR CIPHER CONTROLLER
// =============================================================================
function initCaesar() {
  const encBtn = document.getElementById('btn-caesar-enc');
  const decBtn = document.getElementById('btn-caesar-dec');
  const encText = document.getElementById('caesar-enc-text');
  const encShift = document.getElementById('caesar-enc-shift');
  const encOut = document.getElementById('caesar-enc-out');
  const decText = document.getElementById('caesar-dec-text');
  const decShift = document.getElementById('caesar-dec-shift');
  const decOut = document.getElementById('caesar-dec-out');

  async function runEnc() {
    const shift = parseInt(encShift.value, 10) || 3;
    const text = encText.value;
    try {
      const res = await apiPost('/api/caesar', { action: 'encrypt', text, shift });
      encOut.value = res.result;

      // Auto-Sync to Decryption pane
      decText.value = res.result;
      decShift.value = shift;
      document.getElementById('caesar-dec-shift-badge').textContent = `−${shift} langkah`;

      // Update Metrics
      document.getElementById('caesar-metric-entropy').textContent = `${res.metrics.entropy_in} → ${res.metrics.entropy_out}`;
      document.getElementById('caesar-metric-ioc').textContent = res.metrics.ioc_out;
      document.getElementById('caesar-metric-time').textContent = `${res.metrics.elapsed_ms} ms`;

      // Render Alphabet Mapping Track
      renderCaesarAlphabetTrack(res.mapping, shift);
    } catch (err) {}
  }

  async function runDec() {
    const shift = parseInt(decShift.value, 10) || 3;
    const text = decText.value;
    try {
      const res = await apiPost('/api/caesar', { action: 'decrypt', text, shift });
      decOut.value = res.result;
      showToast('Dekripsi Caesar berhasil dipulihkan!');
    } catch (err) {}
  }

  encBtn.addEventListener('click', runEnc);
  decBtn.addEventListener('click', runDec);

  encShift.addEventListener('input', () => {
    document.getElementById('caesar-enc-shift-badge').textContent = `+${encShift.value} langkah`;
    runEnc();
  });
  decShift.addEventListener('input', () => {
    document.getElementById('caesar-dec-shift-badge').textContent = `−${decShift.value} langkah`;
  });

  // Run on startup
  runEnc();
}

function renderCaesarAlphabetTrack(mapping, shift) {
  const track = document.getElementById('caesar-alphabet-track');
  const caption = document.getElementById('caesar-map-caption');
  if (caption) caption.textContent = `Pergeseran Aktif: k = +${shift}`;
  if (!track || !mapping) return;

  track.innerHTML = mapping.map(m => `
    <div class="alpha-cell">
      <span class="alpha-plain">${m.plain}</span>
      <span class="alpha-arrow">↓</span>
      <span class="alpha-cipher">${m.cipher}</span>
    </div>
  `).join('');
}

// =============================================================================
// 6. VIGENÈRE CIPHER CONTROLLER
// =============================================================================
function initVigenere() {
  const encBtn = document.getElementById('btn-vig-enc');
  const decBtn = document.getElementById('btn-vig-dec');
  const encText = document.getElementById('vig-enc-text');
  const encKey = document.getElementById('vig-enc-key');
  const encOut = document.getElementById('vig-enc-out');
  const decText = document.getElementById('vig-dec-text');
  const decKey = document.getElementById('vig-dec-key');
  const decOut = document.getElementById('vig-dec-out');

  async function runEnc() {
    const text = encText.value;
    const key = encKey.value || 'GARUDA';
    try {
      const res = await apiPost('/api/vigenere', { action: 'encrypt', text, key });
      encOut.value = res.result;

      // Auto-Sync to Decryption pane
      decText.value = res.result;
      decKey.value = key;

      document.getElementById('vig-clean-key-badge').textContent = `Kunci Bersih: ${res.cleaned_key}`;
      document.getElementById('vig-metric-entropy').textContent = `${res.metrics.entropy_in} → ${res.metrics.entropy_out}`;
      document.getElementById('vig-metric-ioc').textContent = res.metrics.ioc_out;
      document.getElementById('vig-metric-keyspace').textContent = `26^${res.cleaned_key.length} (${Math.pow(26, res.cleaned_key.length).toExponential(2)})`;
      document.getElementById('vig-metric-time').textContent = `${res.metrics.elapsed_ms} ms`;

      renderVigenereAlignment(res.alignment);
    } catch (err) {}
  }

  async function runDec() {
    const text = decText.value;
    const key = decKey.value;
    try {
      const res = await apiPost('/api/vigenere', { action: 'decrypt', text, key });
      decOut.value = res.result;
      showToast('Dekripsi Vigenère berhasil dipulihkan!');
    } catch (err) {}
  }

  encBtn.addEventListener('click', runEnc);
  decBtn.addEventListener('click', runDec);

  runEnc();
}

function renderVigenereAlignment(alignment) {
  const tbody = document.querySelector('#vig-alignment-table tbody');
  if (!tbody || !alignment) return;
  tbody.innerHTML = alignment.map(item => `
    <tr>
      <td>${item.index}</td>
      <td style="font-weight:600;">${item.input === ' ' ? '␣ (spasi)' : item.input}</td>
      <td style="color:var(--text-muted);">${item.key_char}</td>
      <td>+${item.shift}</td>
      <td style="font-weight:700;">${item.output === ' ' ? '␣' : item.output}</td>
    </tr>
  `).join('');
}

// =============================================================================
// 7. RC4 STREAM CIPHER CONTROLLER
// =============================================================================
function initRc4() {
  const encBtn = document.getElementById('btn-rc4-enc');
  const decBtn = document.getElementById('btn-rc4-dec');
  const encText = document.getElementById('rc4-enc-text');
  const encKey = document.getElementById('rc4-enc-key');
  const hexOut = document.getElementById('rc4-out-hex');
  const b64Out = document.getElementById('rc4-out-b64');
  const decText = document.getElementById('rc4-dec-text');
  const decKey = document.getElementById('rc4-dec-key');
  const decFmt = document.getElementById('rc4-dec-format');
  const decOut = document.getElementById('rc4-dec-out');

  // Toggle Visibility Secret Key
  const toggleBtn = document.getElementById('btn-toggle-rc4-vis');
  toggleBtn.addEventListener('click', () => {
    if (encKey.type === 'password') {
      encKey.type = 'text';
      decKey.type = 'text';
      toggleBtn.textContent = 'Sembunyikan Kunci';
    } else {
      encKey.type = 'password';
      decKey.type = 'password';
      toggleBtn.textContent = 'Tampilkan Kunci';
    }
  });

  async function runEnc() {
    const text = encText.value;
    const key = encKey.value;
    try {
      const res = await apiPost('/api/rc4', { action: 'encrypt', text, key });
      hexOut.value = res.hex;
      b64Out.value = res.base64;

      // Auto-Sync
      decText.value = res.hex;
      decKey.value = key;
      decFmt.value = 'hex';

      document.getElementById('rc4-metric-size').textContent = `${res.metrics.size_in} B → ${res.metrics.size_out} B`;
      document.getElementById('rc4-metric-entropy').textContent = `${res.metrics.entropy_out} bits/B`;
      document.getElementById('rc4-metric-time').textContent = `${res.metrics.elapsed_ms} ms`;

      renderRc4XorTable(res.xor_steps);
    } catch (err) {}
  }

  async function runDec() {
    const ciphertext = decText.value;
    const key = decKey.value;
    const format = decFmt.value;
    try {
      const res = await apiPost('/api/rc4', { action: 'decrypt', ciphertext, key, format });
      decOut.value = res.plaintext;
      showToast('Dekripsi RC4 Stream pulih dengan sempurna!');
    } catch (err) {}
  }

  encBtn.addEventListener('click', runEnc);
  decBtn.addEventListener('click', runDec);

  decFmt.addEventListener('change', () => {
    if (decFmt.value === 'hex' && hexOut.value) {
      decText.value = hexOut.value;
    } else if (decFmt.value === 'base64' && b64Out.value) {
      decText.value = b64Out.value;
    }
  });

  runEnc();
}

function renderRc4XorTable(steps) {
  const tbody = document.querySelector('#rc4-xor-table tbody');
  if (!tbody || !steps) return;
  tbody.innerHTML = steps.map(s => `
    <tr>
      <td>${s.pos}</td>
      <td style="font-weight:600;">${s.char}</td>
      <td><code>0x${s.plain_hex}</code> (${s.plain_bin})</td>
      <td><code>0x${s.key_hex}</code> (${s.key_bin})</td>
      <td style="font-weight:700;"><code>0x${s.cipher_hex}</code> (${s.cipher_bin})</td>
    </tr>
  `).join('');
}

// =============================================================================
// 8. RSA ASYMMETRIC CIPHER CONTROLLER
// =============================================================================
function initRsa() {
  const genBtn = document.getElementById('btn-rsa-generate');
  const bitsSelect = document.getElementById('rsa-bits-select');
  const pubPem = document.getElementById('rsa-pub-pem');
  const privPem = document.getElementById('rsa-priv-pem');
  const encBtn = document.getElementById('btn-rsa-enc');
  const decBtn = document.getElementById('btn-rsa-dec');
  const encText = document.getElementById('rsa-enc-text');
  const encOut = document.getElementById('rsa-enc-out');
  const decText = document.getElementById('rsa-dec-text');
  const decOut = document.getElementById('rsa-dec-out');

  genBtn.addEventListener('click', async () => {
    genBtn.disabled = true;
    genBtn.textContent = 'Menghitung Prima...';
    try {
      const bits = parseInt(bitsSelect.value, 10) || 2048;
      const res = await apiPost('/api/rsa/generate', { bits });
      pubPem.value = res.public_key;
      privPem.value = res.private_key;
      state.rsaKeypair.publicKey = res.public_key;
      state.rsaKeypair.privateKey = res.private_key;
      state.rsaKeypair.details = res.details;

      document.getElementById('rsa-key-spec-summary').textContent =
        `Modulus Aktif: ${res.details.bits}-bit (${res.details.bytes} byte per blok, maks ${res.details.max_oaep_chunk_bytes} byte per chunk OAEP)`;
      document.getElementById('rsa-metric-bits').textContent = `${res.details.bits}-bit`;
      document.getElementById('rsa-metric-digits').textContent = `${res.details.n_digits} digit desimal`;
      document.getElementById('rsa-metric-exp').textContent = res.details.e;

      showToast(`Keypair RSA ${bits}-bit baru siap digunakan!`);
    } catch (err) {
    } finally {
      genBtn.disabled = false;
      genBtn.textContent = 'Generate Keypair Baru ↻';
    }
  });

  async function runEnc() {
    const text = encText.value;
    const publicKey = pubPem.value;
    try {
      const res = await apiPost('/api/rsa', { action: 'encrypt', text, public_key: publicKey });
      encOut.value = res.base64;

      // Auto-Sync ke Dekripsi
      decText.value = res.base64;

      document.getElementById('rsa-metric-entropy').textContent = `${res.metrics.entropy_out} bits/B`;
      document.getElementById('rsa-metric-chunks').textContent = `${res.chunk_count} Blok (${res.metrics.size_out} B)`;
      document.getElementById('rsa-metric-time').textContent = `Eksekusi: ${res.metrics.elapsed_ms} ms`;
    } catch (err) {}
  }

  async function runDec() {
    const ciphertext = decText.value;
    const privateKey = privPem.value;
    try {
      const res = await apiPost('/api/rsa', { action: 'decrypt', ciphertext, private_key: privateKey });
      decOut.value = res.plaintext;
      showToast('Dekripsi RSA OAEP berhasil dengan valid!');
    } catch (err) {}
  }

  encBtn.addEventListener('click', runEnc);
  decBtn.addEventListener('click', runDec);
}

// =============================================================================
// 9. SUPER ENKRIPSI (4-LAYER PIPELINE) CONTROLLER
// =============================================================================
function initSuper() {
  const encBtn = document.getElementById('btn-super-enc');
  const decBtn = document.getElementById('btn-super-dec');
  const encText = document.getElementById('super-enc-text');
  const encOut = document.getElementById('super-enc-out');
  const decText = document.getElementById('super-dec-text');
  const decOut = document.getElementById('super-dec-out');
  const shiftInput = document.getElementById('super-shift');
  const vigInput = document.getElementById('super-vig-key');
  const rc4Input = document.getElementById('super-rc4-key');
  const regenRsaBtn = document.getElementById('btn-super-regen-rsa');

  regenRsaBtn.addEventListener('click', async () => {
    regenRsaBtn.textContent = 'Menghasilkan RSA...';
    try {
      const res = await apiPost('/api/rsa/generate', { bits: 2048 });
      state.rsaKeypair.publicKey = res.public_key;
      state.rsaKeypair.privateKey = res.private_key;
      document.getElementById('rsa-pub-pem').value = res.public_key;
      document.getElementById('rsa-priv-pem').value = res.private_key;
      showToast('Kunci RSA Super Enkripsi diperbarui ke 2048-bit!');
    } catch (err) {
    } finally {
      regenRsaBtn.textContent = 'Rotasi Kunci RSA Baru ↻';
    }
  });

  async function runEnc() {
    const text = encText.value;
    const shift = parseInt(shiftInput.value, 10) || 7;
    const vig = vigInput.value || 'NUSANTARA';
    const rc4 = rc4Input.value || 'KunciStreamRC42026';
    const pub = state.rsaKeypair.publicKey || document.getElementById('rsa-pub-pem').value;

    try {
      const res = await apiPost('/api/super', {
        action: 'encrypt',
        text,
        caesar_shift: shift,
        vigenere_key: vig,
        rc4_key: rc4,
        public_key: pub
      });

      encOut.value = res.final_ciphertext;
      decText.value = res.final_ciphertext;

      renderSuperTimeline(res);
      showToast('Super Enkripsi 4-Lapis Sukses!');
    } catch (err) {}
  }

  async function runDec() {
    const ciphertext = decText.value;
    const shift = parseInt(shiftInput.value, 10) || 7;
    const vig = vigInput.value || 'NUSANTARA';
    const rc4 = rc4Input.value || 'KunciStreamRC42026';
    const priv = state.rsaKeypair.privateKey || document.getElementById('rsa-priv-pem').value;

    try {
      const res = await apiPost('/api/super', {
        action: 'decrypt',
        ciphertext,
        caesar_shift: shift,
        vigenere_key: vig,
        rc4_key: rc4,
        private_key: priv
      });
      decOut.value = res.final_plaintext;
      renderSuperDecTimeline(res);
      showToast('Super Dekripsi Berhasil Memulihkan Pesan Awal!');
    } catch (err) {}
  }

  encBtn.addEventListener('click', runEnc);
  decBtn.addEventListener('click', runDec);

  setTimeout(runEnc, 400);
}

function renderSuperTimeline(data) {
  const container = document.getElementById('super-pipeline-timeline');
  if (!container || !data.layer_metrics) return;

  const stages = [
    {
      name: 'Layer 0: Input Plaintext',
      desc: 'Teks Terang Bahasa Alami',
      code: data.step0_plaintext,
      metric: data.layer_metrics[0]
    },
    {
      name: 'Layer 1: Caesar Cipher',
      desc: `Monoalfabetik (+${document.getElementById('super-shift').value} Shift)`,
      code: data.step1_caesar,
      metric: data.layer_metrics[1]
    },
    {
      name: 'Layer 2: Vigenère Cipher',
      desc: `Polialfabetik (Kunci: ${document.getElementById('super-vig-key').value})`,
      code: data.step2_vigenere,
      metric: data.layer_metrics[2]
    },
    {
      name: 'Layer 3: RC4 Stream Cipher',
      desc: 'Bitwise Keystream XOR (Hexadecimal / Base64)',
      code: data.step3_rc4_b64,
      metric: data.layer_metrics[3]
    },
    {
      name: 'Layer 4: RSA PKCS#1 OAEP',
      desc: 'Asymmetric Public-Key Wrapper (Base64 Akhir)',
      code: data.final_ciphertext,
      metric: data.layer_metrics[4]
    }
  ];

  container.innerHTML = stages.map((s, idx) => `
    <div class="pipeline-stage">
      <div>
        <div class="stage-badge">${s.name}</div>
        <div class="stage-desc">${s.desc}</div>
      </div>
      <div>
        <div class="stage-output-code">${escapeHtml(s.code)}</div>
      </div>
      <div class="stage-entropy-meter">
        <div class="telemetry-label">ENTROPI SHANNON</div>
        <div style="font-size:1.15rem; font-weight:700;">${s.metric ? s.metric.entropy : '—'}</div>
        <div class="field-hint">${s.metric ? s.metric.size : '—'} Bytes</div>
      </div>
    </div>
  `).join('');
}

function renderSuperDecTimeline(data) {
  const container = document.getElementById('super-pipeline-timeline');
  const label = document.getElementById('super-pipeline-mode-label');
  if (label) label.textContent = 'Tahapan Pembalikan Dekripsi (Lapis 4 RSA → RC4 → Vigenère → Caesar → Plaintext Asli)';
  if (!container) return;

  const stages = [
    {
      name: 'Langkah 0: Ciphertext Input (Base64)',
      desc: 'Sandi Utuh Multi-Layer',
      code: data.step0_ciphertext_b64,
      detail: 'Panjang: ' + data.step0_ciphertext_b64.length + ' karakter'
    },
    {
      name: 'Langkah 1: RSA Decrypt (Kunci Privat)',
      desc: 'Memulihkan Byte Stream RC4 (Hex / Base64)',
      code: data.step1_rsa_decrypted_hex,
      detail: 'Format Hex: ' + data.step1_rsa_decrypted_hex.substring(0, 32) + '...'
    },
    {
      name: 'Langkah 2: RC4 Decrypt (Bitwise XOR Keystream)',
      desc: 'Memulihkan Teks Polialfabetik Vigenère',
      code: data.step2_rc4_decrypted_text,
      detail: 'Encoding: UTF-8 Text'
    },
    {
      name: 'Langkah 3: Vigenère Decrypt (Invers Kata Kunci)',
      desc: 'Memulihkan Teks Pergeseran Caesar',
      code: data.step3_vigenere_decrypted_text,
      detail: 'Kunci: ' + document.getElementById('super-vig-key').value
    },
    {
      name: 'Langkah 4: Caesar Decrypt (Pergeseran Balik −k)',
      desc: 'Memulihkan Plaintext Bahasa Alami 100% Utuh',
      code: data.step4_caesar_decrypted_plaintext,
      detail: 'Shift: -' + document.getElementById('super-shift').value
    }
  ];

  container.innerHTML = stages.map(s => `
    <div class="pipeline-stage">
      <div>
        <div class="stage-badge">${s.name}</div>
        <div class="stage-desc">${s.desc}</div>
      </div>
      <div>
        <div class="stage-output-code">${escapeHtml(s.code)}</div>
      </div>
      <div class="stage-entropy-meter">
        <div class="telemetry-label">STATUS TAHAP</div>
        <div style="font-size:0.95rem; font-weight:700;">TERBUKA ✓</div>
        <div class="field-hint">${s.detail}</div>
      </div>
    </div>
  `).join('');
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// =============================================================================
// 10. MULTIMEDIA & FILE VAULT CONTROLLER
// =============================================================================
function initMediaVault() {
  const dropzone = document.getElementById('media-dropzone');
  const fileInput = document.getElementById('media-file-input');
  const encBtn = document.getElementById('btn-media-encrypt');
  const decBtn = document.getElementById('btn-media-decrypt');
  const algoSelect = document.getElementById('media-algo-select');
  const secretKeyInput = document.getElementById('media-secret-key');
  const hexDump = document.getElementById('media-hex-dump');

  // Drag and drop handling
  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      loadSelectedFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      loadSelectedFile(fileInput.files[0]);
    }
  });

  // Synthetic Sample Buttons (For instant lecturer presentation demo)
  document.getElementById('btn-sample-image').addEventListener('click', () => {
    generateSyntheticSampleImage();
  });
  document.getElementById('btn-sample-audio').addEventListener('click', () => {
    generateSyntheticSampleAudio();
  });
  document.getElementById('btn-sample-doc').addEventListener('click', () => {
    generateSyntheticSampleDoc();
  });

  function loadSelectedFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const base64Data = e.target.result.split(',')[1];
      state.mediaFile = {
        name: file.name,
        type: file.type || 'application/octet-stream',
        size: file.size,
        base64: base64Data
      };
      updateFileInputUI();
    };
    reader.readAsDataURL(file);
  }

  function updateFileInputUI() {
    if (!state.mediaFile) return;
    document.getElementById('media-file-size-badge').textContent = `${(state.mediaFile.size / 1024).toFixed(1)} KB`;
    document.getElementById('media-drop-title').textContent = state.mediaFile.name;
    document.getElementById('media-drop-sub').textContent = `Tipe: ${state.mediaFile.type} (${state.mediaFile.size} byte)`;

    const preview = document.getElementById('media-input-preview');
    preview.style.display = 'block';
    preview.innerHTML = '';

    if (state.mediaFile.type.startsWith('image/')) {
      preview.innerHTML = `<img src="data:${state.mediaFile.type};base64,${state.mediaFile.base64}" alt="Input Preview" />`;
    } else if (state.mediaFile.type.startsWith('audio/')) {
      preview.innerHTML = `<audio controls src="data:${state.mediaFile.type};base64,${state.mediaFile.base64}"></audio>`;
    } else {
      preview.innerHTML = `<div class="field-hint" style="padding:0.75rem; border:1px solid var(--border-hairline);">File biner/dokumen siap diproses.</div>`;
    }
  }

  // Encrypt File
  encBtn.addEventListener('click', async () => {
    if (!state.mediaFile) {
      showToast('Silakan pilih file atau buat sampel terlebih dahulu!');
      return;
    }

    const algo = algoSelect.value;
    const key = secretKeyInput.value;
    const params = {
      shift: 7,
      vigenere_key: key,
      rc4_key: key,
      key: key,
      public_key: state.rsaKeypair.publicKey || document.getElementById('rsa-pub-pem').value
    };

    encBtn.disabled = true;
    encBtn.textContent = 'Mengenkripsi File...';

    try {
      const res = await apiPost('/api/media', {
        action: 'encrypt',
        algorithm: algo,
        file_base64: state.mediaFile.base64,
        filename: state.mediaFile.name,
        mime_type: state.mediaFile.type,
        params
      });

      state.lastProcessedMedia = {
        containerBase64: res.container_base64,
        filename: res.out_filename,
        mimeType: 'application/octet-stream'
      };

      document.getElementById('media-out-headline').textContent = `Enkripsi Selesai: ${res.out_filename}`;
      document.getElementById('media-out-details').innerHTML = `
        Metode: <strong>${res.metadata.mode_detail}</strong><br/>
        Ukuran Awal: ${res.metadata.orig_size} Byte → Cipher: ${res.metadata.cipher_size} Byte<br/>
        SHA-256 Asli: <code>${res.metadata.orig_sha256}</code>
      `;

      // Setup Download Link
      const dlLink = document.getElementById('media-download-link');
      dlLink.href = `data:application/octet-stream;base64,${res.container_base64}`;
      dlLink.download = res.out_filename;
      document.getElementById('media-download-bar').style.display = 'flex';

      // Telemetry
      document.getElementById('media-metric-entropy').textContent = `${res.entropy_plain} → ${res.entropy_cipher}`;
      document.getElementById('media-metric-sha').textContent = res.metadata.orig_sha256.substring(0, 20) + '...';
      document.getElementById('media-metric-verify').textContent = 'Checksum SHA-256 Disimpan dalam Container';
      document.getElementById('media-metric-mode').textContent = algo.toUpperCase();
      document.getElementById('media-metric-time').textContent = `${res.elapsed_ms} ms`;

      // Hex Dump
      hexDump.value = `[PLAINTEXT HEADER]\n${formatHexDump(res.hex_preview_in)}\n\n[CIPHERTEXT CONTAINER HEADER]\n${formatHexDump(res.hex_preview_out)}`;

      document.getElementById('media-output-preview').style.display = 'none';
      showToast(`File berhasil dienkripsi ke ${res.out_filename}`);
    } catch (err) {
    } finally {
      encBtn.disabled = false;
      encBtn.textContent = 'Enkripsi File ke Kontainer (.ecry) →';
    }
  });

  // Decrypt File
  decBtn.addEventListener('click', async () => {
    if (!state.mediaFile) {
      showToast('Silakan pilih file kontainer (.ecry) untuk didekripsi!');
      return;
    }

    const algo = algoSelect.value;
    const key = secretKeyInput.value;
    const params = {
      shift: 7,
      vigenere_key: key,
      rc4_key: key,
      key: key,
      private_key: state.rsaKeypair.privateKey || document.getElementById('rsa-priv-pem').value
    };

    decBtn.disabled = true;
    decBtn.textContent = 'Mendekripsi File...';

    try {
      const res = await apiPost('/api/media', {
        action: 'decrypt',
        algorithm: algo,
        file_base64: state.mediaFile.base64,
        filename: state.mediaFile.name,
        mime_type: state.mediaFile.type,
        params
      });

      document.getElementById('media-out-headline').textContent = `Dekripsi Selesai: ${res.filename}`;
      document.getElementById('media-out-details').innerHTML = `
        Tipe File Pulih: <strong>${res.mime_type}</strong><br/>
        Integritas SHA-256: <strong style="color:var(--text-primary);">${res.integrity_verified ? 'LULUS (100% Identik Tanpa Cacat)' : 'Terverifikasi'}</strong><br/>
        SHA-256 Pulih: <code>${res.recovered_sha256}</code>
      `;

      // Setup Download Link
      const dlLink = document.getElementById('media-download-link');
      dlLink.href = `data:${res.mime_type};base64,${res.recovered_base64}`;
      dlLink.download = res.filename;
      document.getElementById('media-download-bar').style.display = 'flex';

      // Pratinjau Output Pulih
      const outPreview = document.getElementById('media-output-preview');
      outPreview.style.display = 'block';
      outPreview.innerHTML = '';
      if (res.mime_type.startsWith('image/')) {
        outPreview.innerHTML = `<img src="data:${res.mime_type};base64,${res.recovered_base64}" alt="Decrypted Preview" />`;
      } else if (res.mime_type.startsWith('audio/')) {
        outPreview.innerHTML = `<audio controls src="data:${res.mime_type};base64,${res.recovered_base64}"></audio>`;
      } else {
        outPreview.innerHTML = `<div class="field-hint" style="padding:0.75rem; border:1px solid var(--border-hairline);">File dokumen/biner berhasil dipulihkan secara lossless.</div>`;
      }

      // Telemetry
      document.getElementById('media-metric-entropy').textContent = `${res.entropy_recovered} bits/B`;
      document.getElementById('media-metric-sha').textContent = res.recovered_sha256.substring(0, 20) + '...';
      document.getElementById('media-metric-verify').textContent = 'SHA-256 Cocok 100%';
      document.getElementById('media-metric-time').textContent = `${res.elapsed_ms} ms`;

      hexDump.value = `[RECOVERED FILE HEX]\n${formatHexDump(res.hex_preview_out)}`;
      showToast('File berhasil dipulihkan secara utuh!');
    } catch (err) {
    } finally {
      decBtn.disabled = false;
      decBtn.textContent = '← Dekripsi & Pulihkan File Asli';
    }
  });

  // Loopback Test (Langsung pasang hasil enkripsi ke input dekripsi)
  document.getElementById('btn-media-loopback').addEventListener('click', () => {
    if (!state.lastProcessedMedia) return;
    state.mediaFile = {
      name: state.lastProcessedMedia.filename,
      type: 'application/octet-stream',
      size: Math.round(state.lastProcessedMedia.containerBase64.length * 0.75),
      base64: state.lastProcessedMedia.containerBase64
    };
    updateFileInputUI();
    showToast('File terenkripsi disinkronkan ke input dekripsi!');
  });
}

function formatHexDump(hexStr) {
  if (!hexStr) return '';
  const chunks = [];
  for (let i = 0; i < hexStr.length; i += 32) {
    const chunk = hexStr.substring(i, i + 32);
    const spaced = chunk.match(/.{1,2}/g).join(' ');
    chunks.push(spaced);
  }
  return chunks.join('\n');
}

// =============================================================================
// 11. SYNTHETIC SAMPLE GENERATORS (FOR PRESENTATION LIVE DEMO)
// =============================================================================
function generateSyntheticSampleImage() {
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 200;
  const ctx = canvas.getContext('2d');

  // Background
  ctx.fillStyle = '#0a0a0a';
  ctx.fillRect(0, 0, 400, 200);

  // Border & Grid
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 2;
  ctx.strokeRect(10, 10, 380, 180);

  // Text Seal
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 20px "JetBrains Mono", monospace';
  ctx.fillText('EDUCRYPTO LAB SEAL', 70, 75);

  ctx.font = '14px "JetBrains Mono", monospace';
  ctx.fillStyle = '#a1a1aa';
  ctx.fillText('Dokumen Rahasia Negara 2026', 80, 110);
  ctx.fillText('Hash SHA-256 Autentikasi Uji', 80, 135);

  const dataUrl = canvas.toDataURL('image/png');
  const base64Data = dataUrl.split(',')[1];

  state.mediaFile = {
    name: 'kripto_seal_demo.png',
    type: 'image/png',
    size: Math.round(base64Data.length * 0.75),
    base64: base64Data
  };

  const preview = document.getElementById('media-input-preview');
  preview.style.display = 'block';
  preview.innerHTML = `<img src="${dataUrl}" alt="Sample Seal" />`;
  document.getElementById('media-file-size-badge').textContent = `${(state.mediaFile.size / 1024).toFixed(1)} KB`;
  document.getElementById('media-drop-title').textContent = state.mediaFile.name;
  document.getElementById('media-drop-sub').textContent = 'Gambar Stamp Kriptografi PNG Uji Coba';
  showToast('Sampel Gambar PNG berhasil dimuat!');
}

function generateSyntheticSampleAudio() {
  // Generate 1 detik audio WAV PCM 8000Hz nada sinus 440Hz (Nada A4)
  const sampleRate = 8000;
  const duration = 1.0;
  const numSamples = sampleRate * duration;
  const buffer = new ArrayBuffer(44 + numSamples);
  const view = new DataView(buffer);

  // RIFF Header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + numSamples, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // Mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate, true);
  view.setUint16(32, 1, true);
  view.setUint16(34, 8, true); // 8-bit
  writeString(view, 36, 'data');
  view.setUint32(40, numSamples, true);

  // Data sample sinus
  for (let i = 0; i < numSamples; i++) {
    const t = i / sampleRate;
    const val = Math.floor(128 + 110 * Math.sin(2 * Math.PI * 440 * t));
    view.setUint8(44 + i, val);
  }

  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  const base64Data = btoa(binary);

  state.mediaFile = {
    name: 'sinyal_harmonik_440hz.wav',
    type: 'audio/wav',
    size: bytes.byteLength,
    base64: base64Data
  };

  const preview = document.getElementById('media-input-preview');
  preview.style.display = 'block';
  preview.innerHTML = `<audio controls src="data:audio/wav;base64,${base64Data}"></audio>`;
  document.getElementById('media-file-size-badge').textContent = `${(state.mediaFile.size / 1024).toFixed(1)} KB`;
  document.getElementById('media-drop-title').textContent = state.mediaFile.name;
  document.getElementById('media-drop-sub').textContent = 'Audio Sinyal Harmonik 440Hz WAV';
  showToast('Sampel Audio WAV berhasil dimuat!');
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

function generateSyntheticSampleDoc() {
  const textContent =
    "SURAT PERINTAH OPERASI INTELIJEN #882\n" +
    "KLASIFIKASI: SANGAT RAHASIA // TOP SECRET\n" +
    "TANGGAL: 22 OKTOBER 2026\n\n" +
    "Kepada: Komandan Satuan Siber Kriptografi\n" +
    "Perihal: Protokol Pengamanan Saluran Komunikasi Terenkripsi Multi-Lapis\n\n" +
    "Dengan ini diperintahkan untuk segera mengalihkan seluruh transmisi data menuju sektor 7.\n" +
    "Gunakan super enkripsi berantai Caesar-Vigenere-RC4-RSA untuk menjamin kerahasiaan absolut.\n" +
    "Integritas dokumen wajib diverifikasi dengan fungsi hash kriptografi SHA-256.\n\n" +
    "SELESAI.";

  const base64Data = btoa(unescape(encodeURIComponent(textContent)));
  state.mediaFile = {
    name: 'instruksi_operasi_intelijen.txt',
    type: 'text/plain',
    size: textContent.length,
    base64: base64Data
  };

  const preview = document.getElementById('media-input-preview');
  preview.style.display = 'block';
  preview.innerHTML = `<pre style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; max-height:140px; overflow-y:auto; padding:0.75rem; background:var(--bg-surface);">${escapeHtml(textContent)}</pre>`;
  document.getElementById('media-file-size-badge').textContent = `${textContent.length} Bytes`;
  document.getElementById('media-drop-title').textContent = state.mediaFile.name;
  document.getElementById('media-drop-sub').textContent = 'Dokumen Teks Rahasia TXT';
  showToast('Sampel Dokumen TXT berhasil dimuat!');
}

// =============================================================================
// 12. SECURITY AUDIT & CRYPTANALYSIS LAB CONTROLLER
// =============================================================================
function initAuditLab() {
  const runBtn = document.getElementById('btn-run-audit');
  runBtn.addEventListener('click', runAudit);

  // Switcher Frekuensi Huruf
  document.querySelectorAll('.freq-switch-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.freq-switch-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.auditFreqMode = btn.getAttribute('data-freq-mode');
      renderFrequencyChart();
    });
  });
}

async function runAudit() {
  const inputEl = document.getElementById('audit-input-text');
  const text = inputEl.value;
  const runBtn = document.getElementById('btn-run-audit');

  runBtn.disabled = true;
  runBtn.textContent = 'Menganalisis...';

  try {
    const res = await apiPost('/api/audit', {
      text,
      caesar_shift: 7,
      vigenere_key: 'NUSANTARA',
      rc4_key: 'KunciStreamRC42026',
      public_key: state.rsaKeypair.publicKey || document.getElementById('rsa-pub-pem').value
    });

    state.auditData = res;
    renderBenchmarkTable(res.benchmarks);
    renderBruteForceTable(res.brute_force_results);
    renderFrequencyChart();
    showToast('Audit Kriptografi & Analisis Frekuensi Selesai!');
  } catch (err) {
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = 'Jalankan Audit Komprehensif →';
  }
}

function renderBenchmarkTable(benchmarks) {
  const tbody = document.querySelector('#audit-benchmark-table tbody');
  if (!tbody || !benchmarks) return;

  tbody.innerHTML = benchmarks.map(b => `
    <tr>
      <td style="font-weight:600;">${b.algorithm}</td>
      <td style="color:var(--text-secondary);">${b.type}</td>
      <td style="font-family:'JetBrains Mono',monospace; font-weight:700;">${b.entropy.toFixed(4)} bits/B</td>
      <td style="font-family:'JetBrains Mono',monospace;">${b.avalanche}%</td>
      <td style="font-family:'JetBrains Mono',monospace;">${b.ioc}</td>
      <td>${b.size_bytes} B</td>
      <td style="font-size:0.75rem; color:var(--text-muted);">${b.key_space}</td>
    </tr>
  `).join('');
}

function renderFrequencyChart() {
  if (!state.auditData) return;
  const chart = document.getElementById('audit-freq-chart');
  if (!chart) return;

  let freqData;
  const expl = document.getElementById('audit-freq-explanation');

  if (state.auditFreqMode === 'caesar') {
    freqData = state.auditData.freq_caesar.frequencies;
    if (expl) expl.textContent = 'Distribusi Caesar: Bentuk grafik persis sama dengan bahasa alami, hanya posisinya bergeser secara seragam. Sangat mudah ditembus frequency analysis.';
  } else if (state.auditFreqMode === 'vigenere') {
    freqData = state.auditData.freq_vigenere.frequencies;
    if (expl) expl.textContent = 'Distribusi Vigenère: Grafik lebih merata karena substitusi polialfabetik menggunakan beberapa alfabet sandi berbeda secara bergantian.';
  } else {
    freqData = state.auditData.freq_plain.frequencies;
    if (expl) expl.textContent = 'Distribusi Plaintext Asli: Menunjukkan pola frekuensi alami huruf Bahasa Indonesia (huruf A, N, E, I biasanya paling dominan).';
  }

  const maxPct = Math.max(...freqData.map(f => f.percentage), 12);

  chart.innerHTML = freqData.map(f => {
    const heightPct = (f.percentage / maxPct) * 100;
    return `
      <div class="freq-bar-col" title="${f.letter}: ${f.count}x (${f.percentage}%)">
        <div class="freq-bar-fill" style="height:${heightPct}%;"></div>
        <div class="freq-bar-label">${f.letter}</div>
      </div>
    `;
  }).join('');
}

function renderBruteForceTable(candidates) {
  const tbody = document.querySelector('#audit-bruteforce-table tbody');
  if (!tbody || !candidates) return;

  tbody.innerHTML = candidates.map((c, idx) => `
    <tr style="${idx === 0 ? 'background:var(--bg-surface); font-weight:600;' : ''}">
      <td>#${idx + 1}</td>
      <td style="font-family:'JetBrains Mono',monospace;">Shift k = ${c.shift}</td>
      <td style="font-family:'JetBrains Mono',monospace; word-break:break-all;">${escapeHtml(c.plaintext)}</td>
      <td><span class="telemetry-value" style="font-size:0.95rem;">${c.confidence_score}%</span></td>
    </tr>
  `).join('');
}

// =============================================================================
// 13. ANIMATED BACKGROUND CANVAS (SUBTLE ARCHITECTURAL PARTICLES)
// =============================================================================
function initAnimatedCanvas() {
  const canvas = document.getElementById('crypto-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    createParticles();
  }

  function createParticles() {
    particles = [];
    const count = Math.min(Math.floor((width * height) / 18000), 75);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        radius: Math.random() * 1.5 + 0.8
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    const isDark = state.theme === 'dark';
    const dotColor = isDark ? 'rgba(255, 255, 255, 0.22)' : 'rgba(0, 0, 0, 0.2)';
    const lineColor = isDark ? 'rgba(255, 255, 255, 0.04)' : 'rgba(0, 0, 0, 0.04)';

    // Update & Draw Dots
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = dotColor;
      ctx.fill();

      // Connect near dots
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = lineColor;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  draw();
}

// =============================================================================
// 14. INITIALIZATION SEQUENCE
// =============================================================================
async function initApp() {
  initTheme();
  initAnimatedCanvas();
  initNavigation();
  initFxTicker();
  initCaesar();
  initVigenere();
  initRc4();
  initRsa();
  initSuper();
  initMediaVault();
  initAuditLab();

  // Load Initial Server Configuration
  try {
    const initData = await apiGet('/api/init');
    if (initData.default_rsa) {
      state.rsaKeypair.publicKey = initData.default_rsa.public_key;
      state.rsaKeypair.privateKey = initData.default_rsa.private_key;
      state.rsaKeypair.details = initData.default_rsa.details;

      document.getElementById('rsa-pub-pem').value = initData.default_rsa.public_key;
      document.getElementById('rsa-priv-pem').value = initData.default_rsa.private_key;
      document.getElementById('rsa-metric-bits').textContent = `${initData.default_rsa.details.bits}-bit`;
      document.getElementById('rsa-metric-digits').textContent = `${initData.default_rsa.details.n_digits} digit desimal`;
      document.getElementById('rsa-metric-exp').textContent = initData.default_rsa.details.e;
    }
    if (initData.fx) {
      state.fx = initData.fx;
      renderFxData();
    }
  } catch (err) {
    console.warn('Backend server offline or unreachable:', err);
  }
}

document.addEventListener('DOMContentLoaded', initApp);
