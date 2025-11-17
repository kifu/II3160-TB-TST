# Membangun API dasar (FastAPI)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from uuid import UUID

# Import model domain yang telah dibuat
from models import (
    Reservasi,
    InventarisKamarHarian,
    InformasiTamu,
    PeriodeMenginap,
    Harga,
    Ketersediaan,
    StatusReservasi
)

app = FastAPI(
    title="Reservasi Hotel API",
    description="Implementasi Awal (Tahap 4) untuk Proyek II3160",
    version="0.1.0"
)

# --- Database In-Memory Sederhana (untuk simulasi) ---
DB_RESERVASI: dict[UUID, Reservasi] = {}
DB_INVENTARIS: dict[tuple[UUID, date], InventarisKamarHarian] = {}

# --- Helper untuk Inisialisasi Data (Simulasi) ---
def init_db():
    tipe_kamar_deluxe_id = UUID("11111111-1111-1111-1111-111111111111")
    tgl = date(2025, 11, 18)
    
    # Inisialisasi 10 kamar deluxe untuk tanggal 18 Nov 2025
    ketersediaan_awal = Ketersediaan(totalAlokasi=10, jumlahDipesan=0)
    inventaris = InventarisKamarHarian(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        tanggal=tgl,
        tipeKamarId=tipe_kamar_deluxe_id,
        ketersediaan=ketersediaan_awal
    )
    DB_INVENTARIS[(tipe_kamar_deluxe_id, tgl)] = inventaris

init_db()


# --- DTO (Data Transfer Objects) untuk API ---

class BuatReservasiRequest(BaseModel):
    namaTamu: str
    emailTamu: str
    teleponTamu: str
    tipeKamarId: UUID
    tglCheckin: date
    tglCheckOut: date

class ReservasiResponse(BaseModel):
    reservasiId: UUID
    status: str
    namaTamu: str
    tglCheckin: date
    tglCheckOut: date
    harga: Decimal
    mataUang: str

class InventarisResponse(BaseModel):
    tipeKamarId: UUID
    tanggal: date
    totalAlokasi: int
    jumlahDipesan: int
    sisaKetersediaan: int

# --- Endpoint API ---

@app.get("/", tags=["Root"])
def read_root():
    return {"Proyek": "Reservasi Hotel - II3160", "Tahap": 4}

@app.get(
    "/inventaris/{tipe_kamar_id}/{tanggal}",
    response_model=InventarisResponse,
    tags=["Inventaris"]
)
def get_inventaris(tipe_kamar_id: UUID, tanggal: date):
    """
    Endpoint API dasar untuk mengecek ketersediaan (InventarisKamarHarian)
    """
    inventaris = DB_INVENTARIS.get((tipe_kamar_id, tanggal))
    if not inventaris:
        raise HTTPException(status_code=404, detail="Inventaris tidak ditemukan")
    
    return InventarisResponse(
        tipeKamarId=inventaris.tipeKamarId,
        tanggal=inventaris.tanggal,
        totalAlokasi=inventaris.ketersediaan.totalAlokasi,
        jumlahDipesan=inventaris.ketersediaan.jumlahDipesan,
        sisaKetersediaan=inventaris.getKetersediaan()
    )

@app.post(
    "/reservasi",
    response_model=ReservasiResponse,
    status_code=201,
    tags=["Reservasi"]
)
def buat_reservasi_baru(request: BuatReservasiRequest):
    """
    Endpoint API dasar untuk membuat 'Reservasi' baru
    """
    try:
        # 1. Validasi Value Objects
        tamu = InformasiTamu(nama=request.namaTamu, email=request.emailTamu, telepon=request.teleponTamu)
        periode = PeriodeMenginap(tglCheckin=request.tglCheckin, tglCheckOut=request.tglCheckOut)
        
        # 2. Logika Harga Dinamis (Simulasi)
        harga = Harga(jumlah=Decimal("1500000.00"), mataUang="IDR")

        # 3. Cek Ketersediaan (Interaksi antar Aggregates)
        # (Simulasi untuk 1 hari - sesuai data helper)
        if periode.tglCheckin == date(2025, 11, 18) and request.tipeKamarId == UUID("11111111-1111-1111-1111-111111111111"):
            inventaris = DB_INVENTARIS.get((request.tipeKamarId, periode.tglCheckin))
            if not inventaris:
                 raise HTTPException(status_code=400, detail="Inventaris tidak ditemukan untuk tanggal tersebut")
            
            # Cek invariant ketersediaan
            if inventaris.getKetersediaan() < 1:
                raise ValueError("Kamar tidak tersedia") # Akan ditangkap oleh 'except'
            
            # 4. Buat Aggregate Reservasi
            reservasi_baru = Reservasi.buatReservasi(
                tamu=tamu,
                periode=periode,
                tipeKamarId=request.tipeKamarId,
                harga=harga
            )
            
            # 5. Simpan (Commit) perubahan
            inventaris.kurangiKetersediaan(1)
            DB_RESERVASI[reservasi_baru.id] = reservasi_baru
            
            return ReservasiResponse(
                reservasiId=reservasi_baru.id,
                status=reservasi_baru.status.name,
                namaTamu=reservasi_baru.informasiTamu.nama,
                tglCheckin=reservasi_baru.periodeMenginap.tglCheckin,
                tglCheckOut=reservasi_baru.periodeMenginap.tglCheckOut,
                harga=reservasi_baru.harga.jumlah,
                mataUang=reservasi_baru.harga.mataUang
            )
        else:
            raise HTTPException(status_code=400, detail="Kamar tidak tersedia untuk tanggal tersebut (di luar data simulasi)")

    except ValueError as e:
        # Menangkap error dari Value Object (misal tgl checkout < tgl checkin)
        # atau dari invariant (kamar tidak tersedia)
        raise HTTPException(status_code=400, detail=str(e))