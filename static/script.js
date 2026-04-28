/**
 * Sistem Tagihan Listrik PLN — Frontend Logic
 * Handles: golongan tabs, dynamic fields, API calls, struk rendering
 */

// === Daya options per golongan ===
const DAYA_OPTIONS = {
    rumah_tangga: [
        { value: 900, label: '900 VA (R-1) — Rp1.352/kWh' },
        { value: 1300, label: '1.300 VA (R-1) — Rp1.444,70/kWh' },
        { value: 2200, label: '2.200 VA (R-1) — Rp1.444,70/kWh' },
        { value: 3500, label: '3.500 VA (R-2) — Rp1.699,53/kWh' },
        { value: 5500, label: '5.500 VA (R-2) — Rp1.699,53/kWh' },
        { value: 6600, label: '6.600 VA (R-3) — Rp1.699,53/kWh' },
    ],
    bisnis: [
        { value: 6600, label: '6.600 VA (B-2) — Rp1.444,70/kWh', wbp: false },
        { value: 105600, label: '105.600 VA / 105,6 kVA (B-2) — Rp1.444,70/kWh', wbp: false },
        { value: 200000, label: '200.000 VA / 200 kVA (B-2) — Rp1.444,70/kWh', wbp: false },
        { value: 250000, label: '250 kVA (B-3) — WBP/LWBP', wbp: true },
        { value: 555000, label: '555 kVA (B-3) — WBP/LWBP', wbp: true },
    ],
    industri: [
        { value: 250000, label: '250 kVA (I-3) — WBP/LWBP', wbp: true },
        { value: 555000, label: '555 kVA (I-3) — WBP/LWBP', wbp: true },
        { value: 30000000, label: '30.000 kVA (I-4) — Rp996,74/kWh', wbp: true },
    ],
    pemerintah: [
        { value: 6600, label: '6.600 VA (P-1) — Rp1.699,53/kWh', wbp: false },
        { value: 200000, label: '200 kVA (P-1) — Rp1.699,53/kWh', wbp: false },
        { value: 250000, label: '250 kVA (P-2) — WBP/LWBP', wbp: true },
        { value: 555000, label: '555 kVA (P-2) — WBP/LWBP', wbp: true },
    ],
    multiguna: [
        { value: 6600, label: '6.600 VA (L/TR)', wbp: false },
        { value: 66000, label: '66 kVA (L/TM)', wbp: false },
        { value: 200000, label: '200 kVA (L/TT)', wbp: false },
    ],
};

// Which golongan+daya combos need WBP/LWBP fields
function needsWBP(golongan, daya) {
    if (golongan === 'rumah_tangga') return false;
    if (golongan === 'multiguna') return false; // WBP=LWBP, single kWh is fine
    const opts = DAYA_OPTIONS[golongan] || [];
    const opt = opts.find(o => o.value === daya);
    return opt ? opt.wbp : false;
}

function needsKvarh(golongan, daya) {
    if (golongan === 'rumah_tangga') return false;
    if (golongan === 'multiguna') return true;
    if (golongan === 'bisnis') return daya > 200000;
    if (golongan === 'industri') return true;
    if (golongan === 'pemerintah') return daya > 200000;
    return false;
}

// === DOM ===
const form = document.getElementById('billingForm');
const golonganInput = document.getElementById('golongan');
const golonganTabs = document.getElementById('golonganTabs');
const dayaSelect = document.getElementById('daya_terpasang');
const btnSubmit = document.getElementById('btnSubmit');
const btnText = btnSubmit.querySelector('.btn-text');
const btnLoader = btnSubmit.querySelector('.btn-loader');

// === Format ===
function fRp(n) {
    if (n === 0) return 'Rp0';
    const neg = n < 0;
    const f = new Intl.NumberFormat('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(Math.abs(n));
    return (neg ? '-' : '') + 'Rp' + f;
}
function fNum(n) { return new Intl.NumberFormat('id-ID').format(n); }

// === Update daya select ===
function updateDaya(gol) {
    const opts = DAYA_OPTIONS[gol] || [];
    dayaSelect.innerHTML = '';
    opts.forEach((o, i) => {
        const el = document.createElement('option');
        el.value = o.value;
        el.textContent = o.label;
        if (i === 0) el.selected = true;
        dayaSelect.appendChild(el);
    });
}

// === Toggle fields ===
function updateFields(gol) {
    const daya = parseInt(dayaSelect.value) || 0;
    const wbp = needsWBP(gol, daya);
    const kvarh = needsKvarh(gol, daya);

    document.getElementById('field_kwh').style.display = wbp ? 'none' : 'block';
    document.getElementById('field_wbp').style.display = wbp ? 'block' : 'none';
    document.getElementById('field_k').style.display = (wbp && gol !== 'industri') || (gol === 'industri' && daya < 30000000) ? 'block' : 'none';
    document.getElementById('field_kvarh').style.display = kvarh ? 'block' : 'none';
    document.getElementById('field_n').style.display = gol === 'multiguna' ? 'block' : 'none';
    document.getElementById('field_sub_gol').style.display = gol === 'pemerintah' ? 'block' : 'none';

    // Update pemakaian_kwh required state
    document.getElementById('pemakaian_kwh').required = !wbp;
}

// === Tab click ===
golonganTabs.addEventListener('click', (e) => {
    const tab = e.target.closest('.tab');
    if (!tab) return;
    golonganTabs.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const val = tab.dataset.value;
    golonganInput.value = val;
    updateDaya(val);
    updateFields(val);
});

// Daya change also toggles fields
dayaSelect.addEventListener('change', () => updateFields(golonganInput.value));

// Pemerintah sub-golongan change
document.getElementById('sub_golongan').addEventListener('change', (e) => {
    const isP2 = e.target.value === 'P-2';
    // Show WBP fields for P-2
    document.getElementById('field_kwh').style.display = isP2 ? 'none' : 'block';
    document.getElementById('field_wbp').style.display = isP2 ? 'block' : 'none';
    document.getElementById('field_k').style.display = isP2 ? 'block' : 'none';
    document.getElementById('field_kvarh').style.display = isP2 ? 'block' : 'none';
    document.getElementById('pemakaian_kwh').required = !isP2;
});

// === Render struk row ===
function row(label, value, cls = '') {
    return `<div class="struk-row"><span class="struk-label">${label}</span><span class="struk-value ${cls}">${value}</span></div>`;
}

// === Show struk ===
function showStruk(d) {
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('errorState').style.display = 'none';
    const struk = document.getElementById('struk');
    struk.style.display = 'block';

    document.getElementById('strukGolongan').textContent = d.golongan;

    // Info section
    let info = row('ID Pelanggan', d.id_pelanggan);
    info += row('Nama', d.nama);
    info += row('Daya', fNum(d.daya_terpasang) + ' VA (' + d.daya_kva + ' kVA)');
    info += row('Pemakaian', fNum(d.pemakaian_kwh) + ' kWh');
    document.getElementById('strukInfo').innerHTML = info;

    // Biaya section
    let biaya = '';
    if (d.tipe_tarif && d.tipe_tarif.includes('WBP')) {
        if (d.kwh_wbp !== undefined) {
            biaya += row('Tarif WBP', fRp(d.tarif_wbp) + '/kWh');
            biaya += row('Tarif LWBP', fRp(d.tarif_lwbp) + '/kWh');
            if (d.faktor_k && d.faktor_k !== 1.0) biaya += row('Faktor K', d.faktor_k);
            biaya += row('Biaya WBP (' + fNum(d.kwh_wbp) + ' kWh)', fRp(d.biaya_wbp));
            biaya += row('Biaya LWBP (' + fNum(d.kwh_lwbp) + ' kWh)', fRp(d.biaya_lwbp));
        }
        if (d.faktor_n !== undefined) {
            biaya += row('Faktor N', d.faktor_n);
            biaya += row('Tarif Efektif', fRp(d.tarif_efektif) + '/kWh');
            biaya += row('Biaya Pemakaian', fRp(d.tarif_efektif * d.pemakaian_kwh));
        }
    } else {
        biaya += row('Tarif/kWh', fRp(d.tarif_per_kwh));
        biaya += row('Tagihan Dasar', fRp(d.tagihan_dasar));
    }

    // RM
    if (d.rekening_minimum !== undefined) {
        biaya += row('Rekening Minimum', fRp(d.rekening_minimum), d.rm_berlaku ? 'text-orange' : '');
        if (d.rm_berlaku) biaya += row('', '⚠️ RM berlaku (pemakaian di bawah minimum)', 'text-orange small');
    }

    // kVArh
    if (d.denda_kvarh !== undefined && d.denda_kvarh > 0) {
        biaya += row('kVArh Terukur', fNum(d.kvarh_terukur));
        biaya += row('Batas kVArh', fNum(d.batas_kvarh));
        biaya += row('Kelebihan kVArh', fNum(d.kelebihan_kvarh));
        biaya += row('Denda kVArh', '+' + fRp(d.denda_kvarh), 'text-red');
    }
    if (d.power_factor !== undefined && d.pf_status) {
        biaya += row('Power Factor', d.power_factor.toFixed(2) + ' (' + d.pf_status + ')', d.pf_status === 'OK' ? 'text-green' : 'text-red');
    }

    biaya += row('Total Tagihan', fRp(d.total_tagihan));
    document.getElementById('strukBiaya').innerHTML = biaya;

    // Denda section
    let denda = '';
    if (d.denda_keterlambatan > 0) {
        denda += row('Denda (' + d.bulan_terlambat + ' bln × 5%)', '+' + fRp(d.denda_keterlambatan), 'text-red');
    } else {
        denda += row('Denda Keterlambatan', 'Tidak ada', 'text-green');
    }
    document.getElementById('strukDenda').innerHTML = denda;

    document.getElementById('sGrandTotal').textContent = fRp(d.grand_total);
    document.getElementById('sTimestamp').textContent = new Date().toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'medium' });
}

function showError(msg) {
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('struk').style.display = 'none';
    const es = document.getElementById('errorState');
    es.style.display = 'flex';
    document.getElementById('errorMessage').textContent = msg;
}

function setLoading(on) {
    btnSubmit.disabled = on;
    btnText.style.display = on ? 'none' : 'inline';
    btnLoader.style.display = on ? 'inline-block' : 'none';
}

// === Submit ===
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading(true);

    const gol = golonganInput.value;
    const daya = parseInt(dayaSelect.value);
    const wbp = needsWBP(gol, daya);

    const payload = {
        golongan: gol,
        id_pelanggan: document.getElementById('id_pelanggan').value.trim(),
        nama: document.getElementById('nama').value.trim(),
        daya_terpasang: daya,
        pemakaian_kwh: wbp ? 0 : (parseFloat(document.getElementById('pemakaian_kwh').value) || 0),
        hari_terlambat: parseInt(document.getElementById('hari_terlambat').value) || 0,
    };

    if (wbp) {
        payload.kwh_wbp = parseFloat(document.getElementById('kwh_wbp').value) || 0;
        payload.kwh_lwbp = parseFloat(document.getElementById('kwh_lwbp').value) || 0;
        payload.faktor_k = parseFloat(document.getElementById('faktor_k').value) || 1.4;
    }

    if (needsKvarh(gol, daya)) {
        payload.kvarh_terukur = parseFloat(document.getElementById('kvarh_terukur').value) || 0;
        payload.power_factor = parseFloat(document.getElementById('power_factor').value) || 0.85;
    }

    if (gol === 'multiguna') {
        payload.faktor_n = parseFloat(document.getElementById('faktor_n').value) || 1.0;
    }

    if (gol === 'pemerintah') {
        const subGol = document.getElementById('sub_golongan').value;
        payload.sub_golongan = subGol;
        if (subGol === 'P-2') {
            payload.kwh_wbp = parseFloat(document.getElementById('kwh_wbp').value) || 0;
            payload.kwh_lwbp = parseFloat(document.getElementById('kwh_lwbp').value) || 0;
            payload.faktor_k = parseFloat(document.getElementById('faktor_k').value) || 1.4;
            payload.kvarh_terukur = parseFloat(document.getElementById('kvarh_terukur').value) || 0;
            payload.power_factor = parseFloat(document.getElementById('power_factor').value) || 0.85;
            payload.pemakaian_kwh = 0;
        }
    }

    try {
        const res = await fetch('/api/hitung', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await res.json();
        if (!res.ok) showError(data.error || 'Error');
        else showStruk(data);
    } catch (err) {
        showError('Gagal terhubung: ' + err.message);
    } finally {
        setLoading(false);
    }
});

// === Init ===
updateDaya('rumah_tangga');
updateFields('rumah_tangga');
