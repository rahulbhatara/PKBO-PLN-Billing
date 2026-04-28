"""
pelanggan_industri.py — Golongan I (I-3, I-4)

Tarif resmi PLN:
  I-3/TM >200kVA      : WBP=K×1.035,78 | LWBP=1.035,78 | kVArh=1.114,74 (RM tipe **)
  I-4/TT 30.000kVA+   : WBP=LWBP=996,74 | kVArh=996,74 (RM tipe ***)

Catatan:
  RM2 = 40 × kVA × biaya_LWBP
  RM3 = 40 × kVA × biaya_WBP_dan_LWBP
  K: 1.4 ≤ K ≤ 2.0, kVArh berlaku jika PF < 0.85
"""
from .pelanggan_listrik import PelangganListrik


class PelangganIndustri(PelangganListrik):
    """Pelanggan Industri — semua WBP/LWBP + kVArh."""

    TARIF_I3_LWBP = 1035.78
    TARIF_I3_KVARH = 1114.74
    TARIF_I4 = 996.74
    TARIF_I4_KVARH = 996.74
    BATAS_I4 = 30000000  # 30.000 kVA = 30.000.000 VA
    PF_MIN = 0.85
    BATAS_KVARH_FAKTOR = 0.62

    def __init__(self, id_pelanggan, nama, daya_terpasang, pemakaian_kwh,
                 hari_terlambat=0, kwh_wbp=0, kwh_lwbp=0,
                 faktor_k=1.4, kvarh_terukur=0, power_factor=0.85):
        if (kwh_wbp + kwh_lwbp) > 0:
            pemakaian_kwh = kwh_wbp + kwh_lwbp
        super().__init__(id_pelanggan, nama, daya_terpasang, pemakaian_kwh, hari_terlambat)
        self.kwh_wbp = kwh_wbp
        self.kwh_lwbp = kwh_lwbp
        self.faktor_k = max(1.4, min(2.0, faktor_k))
        self.kvarh_terukur = max(0.0, kvarh_terukur)
        self.power_factor = max(0.0, min(1.0, power_factor))

    def _is_i4(self):
        return self.daya_terpasang >= self.BATAS_I4

    def get_golongan(self):
        return "I-4/TT" if self._is_i4() else "I-3/TM"

    def get_tarif_per_kwh(self):
        return self.TARIF_I4 if self._is_i4() else self.TARIF_I3_LWBP

    def _get_tarif_kvarh(self):
        return self.TARIF_I4_KVARH if self._is_i4() else self.TARIF_I3_KVARH

    def hitung_denda_kvarh(self):
        if self.power_factor >= self.PF_MIN:
            return 0.0
        batas = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
        return max(0, self.kvarh_terukur - batas) * self._get_tarif_kvarh()

    def _hitung_rekening_minimum(self):
        if self._is_i4():
            # RM3 = 40 × kVA × biaya_WBP_dan_LWBP
            return self.JAM_NYALA_RM * self._daya_kva() * self.TARIF_I4
        # RM2 = 40 × kVA × biaya_LWBP
        return self.JAM_NYALA_RM * self._daya_kva() * self.TARIF_I3_LWBP

    def hitung_total_tagihan(self):
        rm = self._hitung_rekening_minimum()
        if self._is_i4():
            tagihan = self.pemakaian_kwh * self.TARIF_I4
        else:
            tarif_wbp = self.faktor_k * self.TARIF_I3_LWBP
            tagihan = (self.kwh_wbp * tarif_wbp) + (self.kwh_lwbp * self.TARIF_I3_LWBP)
        tagihan += self.hitung_denda_kvarh()
        return max(tagihan, rm)

    def hitung_denda(self):
        if self.hari_terlambat <= 0:
            return 0.0
        return self.hitung_total_tagihan() * self.PERSEN_DENDA_PER_BULAN * self._hitung_bulan_terlambat()

    def to_dict(self):
        result = super().to_dict()
        is_i4 = self._is_i4()
        tarif_wbp = self.TARIF_I4 if is_i4 else self.faktor_k * self.TARIF_I3_LWBP
        tarif_lwbp = self.TARIF_I4 if is_i4 else self.TARIF_I3_LWBP
        batas_kvarh = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
        rm = self._hitung_rekening_minimum()
        result.update({
            "tipe_tarif": "WBP/LWBP",
            "kwh_wbp": self.kwh_wbp, "kwh_lwbp": self.kwh_lwbp,
            "tarif_wbp": tarif_wbp, "tarif_lwbp": tarif_lwbp,
            "faktor_k": self.faktor_k if not is_i4 else 1.0,
            "biaya_wbp": self.kwh_wbp * tarif_wbp,
            "biaya_lwbp": self.kwh_lwbp * tarif_lwbp,
            "kvarh_terukur": self.kvarh_terukur, "power_factor": self.power_factor,
            "batas_kvarh": batas_kvarh,
            "kelebihan_kvarh": max(0, self.kvarh_terukur - batas_kvarh),
            "denda_kvarh": self.hitung_denda_kvarh(), "tarif_kvarh": self._get_tarif_kvarh(),
            "pf_status": "OK" if self.power_factor >= self.PF_MIN else "BURUK",
            "rekening_minimum": rm,
            "rm_berlaku": self.hitung_total_tagihan() == rm and rm > 0,
            "tipe_rm": "RM3" if is_i4 else "RM2",
        })
        return result
