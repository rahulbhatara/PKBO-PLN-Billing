"""
pelanggan_pemerintah.py — Golongan P (P-1, P-2, P-3)

Tarif resmi PLN:
  P-1/TR 6.600VA s.d. 200kVA : Rp1.699,53/kWh (reguler, RM tipe *)
  P-2/TM >200kVA             : WBP=K×1.415,01 | LWBP=1.415,01 | kVArh=1.522,88 (RM tipe **)
  P-3/TR                     : Rp1.699,53/kWh (reguler, RM tipe *)
"""
from .pelanggan_listrik import PelangganListrik


class PelangganPemerintah(PelangganListrik):
    """Pelanggan Pemerintah — P-1/P-3 (reguler) dan P-2 (WBP/LWBP + kVArh)."""

    TARIF_P1_P3 = 1699.53
    TARIF_P2_LWBP = 1415.01
    TARIF_P2_KVARH = 1522.88
    BATAS_P2 = 200000  # >200 kVA
    PF_MIN = 0.85
    BATAS_KVARH_FAKTOR = 0.62

    def __init__(self, id_pelanggan, nama, daya_terpasang, pemakaian_kwh,
                 hari_terlambat=0, sub_golongan="P-1", kwh_wbp=0, kwh_lwbp=0,
                 faktor_k=1.4, kvarh_terukur=0, power_factor=0.85):
        self.sub_golongan = sub_golongan  # "P-1", "P-2", "P-3"
        if self._is_p2() and (kwh_wbp + kwh_lwbp) > 0:
            pemakaian_kwh = kwh_wbp + kwh_lwbp
        super().__init__(id_pelanggan, nama, daya_terpasang, pemakaian_kwh, hari_terlambat)
        self.kwh_wbp = kwh_wbp
        self.kwh_lwbp = kwh_lwbp
        self.faktor_k = max(1.4, min(2.0, faktor_k))
        self.kvarh_terukur = max(0.0, kvarh_terukur)
        self.power_factor = max(0.0, min(1.0, power_factor))

    def _is_p2(self):
        return self.sub_golongan == "P-2"

    def get_golongan(self):
        if self._is_p2():
            return "P-2/TM"
        if self.sub_golongan == "P-3":
            return "P-3/TR"
        return "P-1/TR"

    def get_tarif_per_kwh(self):
        return self.TARIF_P2_LWBP if self._is_p2() else self.TARIF_P1_P3

    def hitung_denda_kvarh(self):
        if not self._is_p2() or self.power_factor >= self.PF_MIN:
            return 0.0
        batas = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
        return max(0, self.kvarh_terukur - batas) * self.TARIF_P2_KVARH

    def _hitung_rekening_minimum(self):
        if self._is_p2():
            return self.JAM_NYALA_RM * self._daya_kva() * self.TARIF_P2_LWBP
        return self.JAM_NYALA_RM * self._daya_kva() * self.TARIF_P1_P3

    def hitung_total_tagihan(self):
        rm = self._hitung_rekening_minimum()
        if self._is_p2():
            tarif_wbp = self.faktor_k * self.TARIF_P2_LWBP
            tagihan = (self.kwh_wbp * tarif_wbp) + (self.kwh_lwbp * self.TARIF_P2_LWBP)
            tagihan += self.hitung_denda_kvarh()
        else:
            tagihan = self.TARIF_P1_P3 * self.pemakaian_kwh
        return max(tagihan, rm)

    def hitung_denda(self):
        if self.hari_terlambat <= 0:
            return 0.0
        return self.hitung_total_tagihan() * self.PERSEN_DENDA_PER_BULAN * self._hitung_bulan_terlambat()

    def to_dict(self):
        result = super().to_dict()
        rm = self._hitung_rekening_minimum()
        result["rekening_minimum"] = rm
        result["rm_berlaku"] = self.hitung_total_tagihan() == rm and rm > 0
        if self._is_p2():
            tarif_wbp = self.faktor_k * self.TARIF_P2_LWBP
            batas_kvarh = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
            result.update({
                "tipe_tarif": "WBP/LWBP",
                "kwh_wbp": self.kwh_wbp, "kwh_lwbp": self.kwh_lwbp,
                "tarif_wbp": tarif_wbp, "tarif_lwbp": self.TARIF_P2_LWBP,
                "faktor_k": self.faktor_k,
                "biaya_wbp": self.kwh_wbp * tarif_wbp,
                "biaya_lwbp": self.kwh_lwbp * self.TARIF_P2_LWBP,
                "kvarh_terukur": self.kvarh_terukur, "power_factor": self.power_factor,
                "batas_kvarh": batas_kvarh,
                "kelebihan_kvarh": max(0, self.kvarh_terukur - batas_kvarh),
                "denda_kvarh": self.hitung_denda_kvarh(), "tarif_kvarh": self.TARIF_P2_KVARH,
                "pf_status": "OK" if self.power_factor >= self.PF_MIN else "BURUK",
            })
        else:
            result["tipe_tarif"] = "Reguler"
        return result
