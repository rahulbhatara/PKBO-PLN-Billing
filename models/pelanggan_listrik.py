"""
pelanggan_listrik.py — Abstract Base Class untuk semua golongan pelanggan PLN.

ABSTRAKSI: Class ini mendefinisikan kontrak yang harus dipenuhi setiap golongan.
Setiap golongan WAJIB mengimplementasi method abstrak karena rumus perhitungan
tagihan, denda, dan rekening minimum BERBEDA untuk setiap golongan.

Data referensi: tarif_pln.md (Tarif Tenaga Listrik resmi PLN)
"""
from abc import ABC, abstractmethod


class PelangganListrik(ABC):
    """Abstract Base Class untuk semua golongan pelanggan listrik PLN."""

    PERSEN_DENDA_PER_BULAN = 0.05  # 5% per bulan keterlambatan
    MAKS_BULAN_DENDA = 6
    JAM_NYALA_RM = 40  # Jam nyala untuk Rekening Minimum

    def __init__(self, id_pelanggan: str, nama: str, daya_terpasang: int,
                 pemakaian_kwh: float, hari_terlambat: int = 0):
        if pemakaian_kwh < 0:
            raise ValueError("Pemakaian kWh tidak boleh negatif")
        if daya_terpasang <= 0:
            raise ValueError("Daya terpasang harus lebih dari 0")
        if hari_terlambat < 0:
            raise ValueError("Hari terlambat tidak boleh negatif")

        self.id_pelanggan = id_pelanggan
        self.nama = nama
        self.daya_terpasang = daya_terpasang  # dalam VA
        self.pemakaian_kwh = pemakaian_kwh
        self.hari_terlambat = hari_terlambat

    # === ABSTRACT METHODS — wajib di-override ===

    @abstractmethod
    def hitung_total_tagihan(self) -> float:
        """Hitung tagihan (sudah termasuk RM jika berlaku)."""
        pass

    @abstractmethod
    def hitung_denda(self) -> float:
        """Hitung denda keterlambatan."""
        pass

    @abstractmethod
    def get_golongan(self) -> str:
        """Nama golongan tarif (contoh: 'R-1/TR', 'B-3/TM, TT')."""
        pass

    @abstractmethod
    def get_tarif_per_kwh(self) -> float:
        """Tarif dasar per kWh (untuk reguler) atau LWBP (untuk WBP/LWBP)."""
        pass

    # === CONCRETE METHODS ===

    def _daya_kva(self) -> float:
        """Konversi daya dari VA ke kVA."""
        return self.daya_terpasang / 1000.0

    def _hitung_bulan_terlambat(self) -> int:
        """Konversi hari terlambat ke bulan (pembulatan atas), maks 6."""
        bulan = (self.hari_terlambat + 29) // 30
        return min(bulan, self.MAKS_BULAN_DENDA)

    def hitung_grand_total(self) -> float:
        """Grand total = tagihan + denda keterlambatan."""
        return self.hitung_total_tagihan() + self.hitung_denda()

    def to_dict(self) -> dict:
        """Serialize ke dict untuk JSON API response."""
        tagihan = self.hitung_total_tagihan()
        denda = self.hitung_denda()
        return {
            "golongan": self.get_golongan(),
            "id_pelanggan": self.id_pelanggan,
            "nama": self.nama,
            "daya_terpasang": self.daya_terpasang,
            "daya_kva": self._daya_kva(),
            "pemakaian_kwh": self.pemakaian_kwh,
            "tarif_per_kwh": self.get_tarif_per_kwh(),
            "tagihan_dasar": self.get_tarif_per_kwh() * self.pemakaian_kwh,
            "total_tagihan": tagihan,
            "hari_terlambat": self.hari_terlambat,
            "bulan_terlambat": self._hitung_bulan_terlambat() if self.hari_terlambat > 0 else 0,
            "denda_keterlambatan": denda,
            "grand_total": tagihan + denda,
        }
