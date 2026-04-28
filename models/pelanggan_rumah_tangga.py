"""
pelanggan_rumah_tangga.py — Golongan R (R-1, R-2, R-3)

Tarif resmi PLN:
  R-1/TR 900VA RTM   : Rp1.352,00/kWh
  R-1/TR 1.300VA      : Rp1.444,70/kWh
  R-1/TR 2.200VA      : Rp1.444,70/kWh
  R-2/TR 3.500-5.500VA: Rp1.699,53/kWh
  R-3/TR,TM 6.600VA+  : Rp1.699,53/kWh

Rekening Minimum (RM1):
  RM1 = 40 × daya_kVA × biaya_pemakaian
"""
from .pelanggan_listrik import PelangganListrik


class PelangganRumahTangga(PelangganListrik):
    """Pelanggan Rumah Tangga — tarif flat, RM tipe *) ."""

    TARIF = {900: 1352.00, 1300: 1444.70, 2200: 1444.70}
    TARIF_R2_R3 = 1699.53

    def get_golongan(self):
        if self.daya_terpasang <= 2200:
            return f"R-1/TR ({self.daya_terpasang} VA)"
        elif self.daya_terpasang <= 5500:
            return "R-2/TR"
        return "R-3/TR, TM"

    def get_tarif_per_kwh(self):
        if self.daya_terpasang in self.TARIF:
            return self.TARIF[self.daya_terpasang]
        return 1444.70 if self.daya_terpasang <= 2200 else self.TARIF_R2_R3

    def _hitung_rekening_minimum(self):
        """RM1 = 40 × daya_kVA × biaya_pemakaian."""
        return self.JAM_NYALA_RM * self._daya_kva() * self.get_tarif_per_kwh()

    def hitung_total_tagihan(self):
        tagihan = self.get_tarif_per_kwh() * self.pemakaian_kwh
        rm = self._hitung_rekening_minimum()
        return max(tagihan, rm)  # Tagihan minimal = RM

    def hitung_denda(self):
        if self.hari_terlambat <= 0:
            return 0.0
        bulan = self._hitung_bulan_terlambat()
        return self.hitung_total_tagihan() * self.PERSEN_DENDA_PER_BULAN * bulan

    def to_dict(self):
        result = super().to_dict()
        rm = self._hitung_rekening_minimum()
        tagihan_normal = self.get_tarif_per_kwh() * self.pemakaian_kwh
        result.update({
            "tipe_tarif": "Reguler",
            "rekening_minimum": rm,
            "rm_berlaku": tagihan_normal < rm,
        })
        return result
