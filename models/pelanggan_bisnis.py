"""
pelanggan_bisnis.py — Golongan B (B-2, B-3)

Tarif resmi PLN:
  B-2/TR 6.600VA s.d. 200kVA : Rp1.444,70/kWh (reguler, RM tipe *)
  B-3/TM,TT >200kVA          : WBP=K×1.035,78 | LWBP=1.035,78 | kVArh=1.114,74 (RM tipe **)

Catatan:
  RM1 = 40 × daya_kVA × biaya_pemakaian
  RM2 = 40 × daya_kVA × biaya_pemakaian_LWBP
  K: 1.4 ≤ K ≤ 2.0, kVArh berlaku jika PF < 0.85
"""
from .pelanggan_listrik import PelangganListrik


class PelangganBisnis(PelangganListrik):
    """Pelanggan Bisnis — B-2 (reguler) dan B-3 (WBP/LWBP + kVArh)."""

    TARIF_B2 = 1444.70
    TARIF_B3_LWBP = 1035.78
    TARIF_B3_KVARH = 1114.74
    BATAS_B3 = 200000  # >200 kVA
    PF_MIN = 0.85
    BATAS_KVARH_FAKTOR = 0.62

    def __init__(self, id_pelanggan, nama, daya_terpasang, pemakaian_kwh,
                 hari_terlambat=0, kwh_wbp=0, kwh_lwbp=0,
                 faktor_k=1.4, kvarh_terukur=0, power_factor=0.85):
        if daya_terpasang > self.BATAS_B3 and (kwh_wbp + kwh_lwbp) > 0:
            pemakaian_kwh = kwh_wbp + kwh_lwbp
        super().__init__(id_pelanggan, nama, daya_terpasang, pemakaian_kwh, hari_terlambat)
        self.kwh_wbp = kwh_wbp
        self.kwh_lwbp = kwh_lwbp
        self.faktor_k = max(1.4, min(2.0, faktor_k))
        self.kvarh_terukur = max(0.0, kvarh_terukur)
        self.power_factor = max(0.0, min(1.0, power_factor))

    def _is_b3(self):
        return self.daya_terpasang > self.BATAS_B3

    def get_golongan(self):
        return "B-3/TM, TT" if self._is_b3() else "B-2/TR"

    def get_tarif_per_kwh(self):
        return self.TARIF_B3_LWBP if self._is_b3() else self.TARIF_B2

    def hitung_denda_kvarh(self):
        if not self._is_b3() or self.power_factor >= self.PF_MIN:
            return 0.0
        batas = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
        return max(0, self.kvarh_terukur - batas) * self.TARIF_B3_KVARH

    def _hitung_rekening_minimum(self):
        if self._is_b3():
            # RM2 = 40 × kVA × LWBP
            return self.JAM_NYALA_RM * self._daya_kva() * self.TARIF_B3_LWBP
        # RM1 = 40 × kVA × biaya_pemakaian
        return self.JAM_NYALA_RM * self._daya_kva() * self.TARIF_B2

    def hitung_total_tagihan(self):
        rm = self._hitung_rekening_minimum()
        if self._is_b3():
            tarif_wbp = self.faktor_k * self.TARIF_B3_LWBP
            tagihan = (self.kwh_wbp * tarif_wbp) + (self.kwh_lwbp * self.TARIF_B3_LWBP)
            tagihan += self.hitung_denda_kvarh()
        else:
            tagihan = self.TARIF_B2 * self.pemakaian_kwh
        return max(tagihan, rm)

    def hitung_denda(self):
        if self.hari_terlambat <= 0:
            return 0.0
        return self.hitung_total_tagihan() * self.PERSEN_DENDA_PER_BULAN * self._hitung_bulan_terlambat()

    def to_dict(self):
        result = super().to_dict()
        rm = self._hitung_rekening_minimum()
        if self._is_b3():
            tarif_wbp = self.faktor_k * self.TARIF_B3_LWBP
            batas_kvarh = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
            result.update({
                "tipe_tarif": "WBP/LWBP",
                "kwh_wbp": self.kwh_wbp, "kwh_lwbp": self.kwh_lwbp,
                "tarif_wbp": tarif_wbp, "tarif_lwbp": self.TARIF_B3_LWBP,
                "faktor_k": self.faktor_k,
                "biaya_wbp": self.kwh_wbp * tarif_wbp,
                "biaya_lwbp": self.kwh_lwbp * self.TARIF_B3_LWBP,
                "kvarh_terukur": self.kvarh_terukur, "power_factor": self.power_factor,
                "batas_kvarh": batas_kvarh,
                "kelebihan_kvarh": max(0, self.kvarh_terukur - batas_kvarh),
                "denda_kvarh": self.hitung_denda_kvarh(), "tarif_kvarh": self.TARIF_B3_KVARH,
                "pf_status": "OK" if self.power_factor >= self.PF_MIN else "BURUK",
            })
        else:
            result["tipe_tarif"] = "Reguler"
        result.update({"rekening_minimum": rm, "rm_berlaku": self.hitung_total_tagihan() == rm and rm > 0})
        return result
