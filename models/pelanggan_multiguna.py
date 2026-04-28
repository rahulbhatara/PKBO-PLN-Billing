"""
pelanggan_multiguna.py — Golongan L (Curah/Multiguna/Lampu Jalan)

Tarif resmi PLN:
  L/TR, TM, TT : WBP dan LWBP = N × 1.644,52 | kVArh = N × 1.644,52

Catatan:
  N = faktor pengali yang ditetapkan PLN (bervariasi).
  Tidak ada RM khusus (biaya beban = - ).
  kVArh berlaku jika PF < 0.85.
"""
from .pelanggan_listrik import PelangganListrik


class PelangganMultiguna(PelangganListrik):
    """Pelanggan Multiguna/Curah (L) — tarif WBP=LWBP dengan faktor N."""

    TARIF_DASAR = 1644.52
    PF_MIN = 0.85
    BATAS_KVARH_FAKTOR = 0.62

    def __init__(self, id_pelanggan, nama, daya_terpasang, pemakaian_kwh,
                 hari_terlambat=0, faktor_n=1.0,
                 kvarh_terukur=0, power_factor=0.85):
        super().__init__(id_pelanggan, nama, daya_terpasang, pemakaian_kwh, hari_terlambat)
        self.faktor_n = max(0.0, faktor_n)
        self.kvarh_terukur = max(0.0, kvarh_terukur)
        self.power_factor = max(0.0, min(1.0, power_factor))

    def get_golongan(self):
        return "L/TR, TM, TT"

    def get_tarif_per_kwh(self):
        return self.faktor_n * self.TARIF_DASAR

    def _get_tarif_kvarh(self):
        return self.faktor_n * self.TARIF_DASAR

    def hitung_denda_kvarh(self):
        if self.power_factor >= self.PF_MIN:
            return 0.0
        batas = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
        return max(0, self.kvarh_terukur - batas) * self._get_tarif_kvarh()

    def hitung_total_tagihan(self):
        # WBP = LWBP = N × 1.644,52 (tarif sama untuk semua waktu)
        tarif = self.get_tarif_per_kwh()
        tagihan = tarif * self.pemakaian_kwh
        return tagihan + self.hitung_denda_kvarh()

    def hitung_denda(self):
        if self.hari_terlambat <= 0:
            return 0.0
        return self.hitung_total_tagihan() * self.PERSEN_DENDA_PER_BULAN * self._hitung_bulan_terlambat()

    def to_dict(self):
        result = super().to_dict()
        batas_kvarh = self.pemakaian_kwh * self.BATAS_KVARH_FAKTOR
        result.update({
            "tipe_tarif": "WBP/LWBP (N)",
            "faktor_n": self.faktor_n,
            "tarif_efektif": self.get_tarif_per_kwh(),
            "kvarh_terukur": self.kvarh_terukur, "power_factor": self.power_factor,
            "batas_kvarh": batas_kvarh,
            "kelebihan_kvarh": max(0, self.kvarh_terukur - batas_kvarh),
            "denda_kvarh": self.hitung_denda_kvarh(),
            "tarif_kvarh": self._get_tarif_kvarh(),
            "pf_status": "OK" if self.power_factor >= self.PF_MIN else "BURUK",
        })
        return result
