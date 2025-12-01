import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import model domain
from models import (
    Reservasi,
    InventarisKamarHarian,
    InformasiTamu,
    PeriodeMenginap,
    Harga,
    Ketersediaan
)

app = FastAPI(
    title="Reservasi Hotel API",
    description="Implementasi Lanjutan (Tahap 5) - Autentikasi JWT",
    version="0.2.0"
)

# --- Konfigurasi Keamanan (JWT) ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto") 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Database User Dummy (Untuk Simulasi) ---
users_db = {
    "saikul666": {
        "username": "saikul666",
        "full_name": "Saikul Mubaraq",
        "email": "saikulmubaraq@gmail.com",
        "hashed_password": pwd_context.hash("rahasia666"), 
        "disabled": False,
    }
}

# --- Database Domain In-Memory ---
DB_RESERVASI: dict[UUID, Reservasi] = {}
DB_INVENTARIS: dict[tuple[UUID, date], InventarisKamarHarian] = {}

def init_db():
    tipe_kamar_deluxe_id = UUID("11111111-1111-1111-1111-111111111111")
    tgl = date(2025, 11, 18)
    
    # Inisialisasi 10 kamar deluxe
    ketersediaan_awal = Ketersediaan(totalAlokasi=10, jumlahDipesan=0)
    inventaris = InventarisKamarHarian(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        tanggal=tgl,
        tipeKamarId=tipe_kamar_deluxe_id,
        ketersediaan=ketersediaan_awal
    )
    DB_INVENTARIS[(tipe_kamar_deluxe_id, tgl)] = inventaris

init_db()

# --- Model & Helper Autentikasi ---

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

# --- DTO API ---

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
    return {"Proyek": "Reservasi Hotel - II3160", "Tahap": 5, "Status": "Secure"}

# --- Endpoint Autentikasi (Login) ---
@app.post("/token", response_model=Token, tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoint Inventaris (Public) ---
@app.get(
    "/inventaris/{tipe_kamar_id}/{tanggal}",
    response_model=InventarisResponse,
    tags=["Inventaris"]
)
def get_inventaris(tipe_kamar_id: UUID, tanggal: date):
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

# --- Endpoint Reservasi (Protected) ---
@app.post(
    "/reservasi",
    response_model=ReservasiResponse,
    status_code=201,
    tags=["Reservasi"]
)
def buat_reservasi_baru(
    request: BuatReservasiRequest,
    current_user: User = Depends(get_current_user) # Proteksi Endpoint
):
    """
    Endpoint untuk membuat reservasi baru.
    REQUIRES AUTHENTICATION (Login terlebih dahulu di /token)
    """
    try:
        tamu = InformasiTamu(nama=request.namaTamu, email=request.emailTamu, telepon=request.teleponTamu)
        periode = PeriodeMenginap(tglCheckin=request.tglCheckin, tglCheckOut=request.tglCheckOut)
        harga = Harga(jumlah=Decimal("1500000.00"), mataUang="IDR")

        if periode.tglCheckin == date(2025, 11, 18) and request.tipeKamarId == UUID("11111111-1111-1111-1111-111111111111"):
            inventaris = DB_INVENTARIS.get((request.tipeKamarId, periode.tglCheckin))
            if not inventaris:
                 raise HTTPException(status_code=400, detail="Inventaris tidak ditemukan")
            
            if inventaris.getKetersediaan() < 1:
                raise ValueError("Kamar tidak tersedia")
            
            reservasi_baru = Reservasi.buatReservasi(tamu, periode, request.tipeKamarId, harga)
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
            raise HTTPException(status_code=400, detail="Kamar tidak tersedia (Simulasi terbatas tgl 18 Nov)")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))