# Tugas Final Project II3160 - Teknologi Sistem Terintegrasi

# Domain: Reservasi Hotel (DDD)

Repositori ini berisi pengerjaan Tugas Final Project untuk mata kuliah II3160 - Teknologi Sistem Terintegrasi. Proyek ini berfokus pada perancangan dan implementasi sistem **Reservasi Hotel** menggunakan pendekatan **Domain-Driven Design (DDD)**.

**Author:**

- **Nama:** Andi Syaichul Mubaraq
- **NIM:** 18223139

---

## 📍 Fokus Proyek

Implementasi saat ini telah mencapai **Tahap 5 (Implementasi Lanjutan)**. Fokus utama tahap ini adalah melengkapi **Reservasi Context** dengan lapisan keamanan dan autentikasi.

**Fitur & Aggregates yang Diimplementasikan:**

1.  **Reservasi (Aggregate)**: Mengelola siklus hidup pemesanan, dari `DIPESAN` hingga `SELESAI`.
2.  **InventarisKamarHarian (Aggregate)**: Mengelola ketersediaan kamar secara transaksional untuk tanggal tertentu dan melindungi _invariant_ alokasi.
3.  **Keamanan (Auth)**:
    -   Implementasi **JWT (JSON Web Token)** untuk autentikasi pengguna.
    -   Proteksi endpoint sensitif (`POST /reservasi`) menggunakan dependency injection.
    -   Penggunaan algoritma **Argon2** untuk hashing password yang aman dan modern.

## 🛠️ Teknologi yang Digunakan

-   **Bahasa:** Python 3.10+ (Mendukung hingga Python 3.14)
-   **Framework API:** FastAPI
-   **Server:** Uvicorn
-   **Keamanan:**
    -   `python-jose` (Generate & Validasi Token)
    -   `passlib` (Manajemen Password)
    -   `argon2-cffi` (Algoritma Hashing)

## 🚀 Cara Menjalankan Proyek

### 1. Prasyarat

Pastikan Anda memiliki Python 3.10 atau yang lebih baru terinstal di sistem Anda.

### 2. Instalasi

1.  Clone repositori ini (atau unduh file `main.py` dan `models.py`).
2.  Buka terminal di folder proyek.
3.  Instal _library_ yang dibutuhkan (termasuk dependencies keamanan):
    ```bash
    pip install fastapi "uvicorn[standard]" python-jose[cryptography] passlib argon2-cffi
    ```

### 3. Menjalankan Server

Jalankan server API menggunakan Uvicorn dari terminal Anda:

```bash
uvicorn main:app --reload
```

Untuk melihat dokumentasi API, ketik alamat berikut di address bar browser web:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
