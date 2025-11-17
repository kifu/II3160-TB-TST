# Menerjemahkan Desain Taktis (Tahap 3) ke dalam kode.

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

# --- Enum dari Desain Taktis ---

class StatusReservasi(Enum):
    DIPESAN = "DIPESAN"
    DIKONFIRMASI = "DIKONFIRMASI"
    DIBATALKAN = "DIBATALKAN"
    CHECKED_IN = "CHECKED_IN"
    SELESAI = "SELESAI"


# --- Value Objects dari Desain Taktis ---

@dataclass(frozen=True)
class InformasiTamu:
    nama: str
    email: str
    telepon: str

@dataclass(frozen=True)
class PeriodeMenginap:
    tglCheckin: date
    tglCheckOut: date

    def __post_init__(self):
        # Melindungi Invarian: Tanggal Check-Out harus setelah Tanggal Check-In 
        if self.tglCheckOut <= self.tglCheckin:
            raise ValueError("Tanggal Check-Out harus setelah Tanggal Check-In")

@dataclass(frozen=True)
class Harga:
    jumlah: Decimal
    mataUang: str

@dataclass
class Ketersediaan:
    totalAlokasi: int
    jumlahDipesan: int

    def kurangi(self, jumlah: int):
        # Melindungi Invarian: Jumlah dipesan tidak boleh melebihi total alokasi
        if (self.jumlahDipesan + jumlah) > self.totalAlokasi:
            raise ValueError("Ketersediaan kamar tidak mencukupi")
        self.jumlahDipesan += jumlah

    def tambah(self, jumlah: int):
        # Digunakan saat ada pembatalan
        self.jumlahDipesan = max(0, self.jumlahDipesan - jumlah)

    @property
    def sisa(self) -> int:
        return self.totalAlokasi - self.jumlahDipesan

# --- Aggregates dari Desain Taktis ---

class Reservasi:
    def __init__(
        self,
        id: UUID,
        status: StatusReservasi,
        tipeKamarId: UUID,
        informasiTamu: InformasiTamu,
        periodeMenginap: PeriodeMenginap,
        harga: Harga
    ):
        self.id = id 
        self.status = status 
        self.tipeKamarId = tipeKamarId 
        self.informasiTamu = informasiTamu 
        self.periodeMenginap = periodeMenginap 
        self.harga = harga 

    @staticmethod
    def buatReservasi(
        tamu: InformasiTamu,
        periode: PeriodeMenginap,
        tipeKamarId: UUID,
        harga: Harga
    ) -> 'Reservasi':
        return Reservasi(
            id=uuid4(),
            status=StatusReservasi.DIPESAN,
            tipeKamarId=tipeKamarId,
            informasiTamu=tamu,
            periodeMenginap=periode,
            harga=harga
        )

    def konfirmasi(self):
        if self.status == StatusReservasi.DIPESAN:
            self.status = StatusReservasi.DIKONFIRMASI
        else:
            raise ValueError(f"Reservasi dengan status {self.status.name} tidak dapat dikonfirmasi")

    def batalkan(self): 
        if self.status in [StatusReservasi.CHECKED_IN, StatusReservasi.SELESAI]:
            raise ValueError(f"Reservasi dengan status {self.status.name} tidak dapat dibatalkan")
        self.status = StatusReservasi.DIBATALKAN

    def checkin(self): 
        if self.status == StatusReservasi.DIKONFIRMASI:
            self.status = StatusReservasi.CHECKED_IN
        else:
            raise ValueError(f"Hanya reservasi DIKONFIRMASI yang dapat check-in")


class InventarisKamarHarian:
    def __init__(
        self,
        id: UUID,
        tanggal: date,
        tipeKamarId: UUID,
        ketersediaan: Ketersediaan
    ):
        self.id = id 
        self.tanggal = tanggal 
        self.tipeKamarId = tipeKamarId 
        self.ketersediaan = ketersediaan 

    def kurangiKetersediaan(self, jumlah: int = 1): 
        self.ketersediaan.kurangi(jumlah)

    def tambahKetersediaan(self, jumlah: int = 1): 
        self.ketersediaan.tambah(jumlah)

    def getKetersediaan(self) -> int: 
        return self.ketersediaan.sisa