# Tugas Final Project II3160 - Teknologi Sistem Terintegrasi

# Domain: Reservasi Hotel (DDD)

Repositori ini berisi pengerjaan Tugas Final Project untuk mata kuliah II3160 - Teknologi Sistem Terintegrasi. Proyek ini berfokus pada perancangan dan implementasi sistem **Reservasi Hotel** menggunakan pendekatan **Domain-Driven Design (DDD)**.

**Author:**

- **Nama:** Andi Syaichul Mubaraq
- **NIM:** 18223139

---

## 📍 Fokus Proyek

Implementasi saat ini berfokus pada **Reservasi Context**, yang telah diidentifikasi sebagai _Core Domain_.

Tujuan tahap ini adalah menerjemahkan Desain Taktis (Aggregates, Value Objects) ke dalam kode Python yang fungsional dan menyediakan API dasar menggunakan FastAPI.

**Aggregates yang Diimplementasikan:**

1.  **Reservasi**: Mengelola siklus hidup pemesanan, dari `DIPESAN` hingga `SELESAI`.
2.  **InventarisKamarHarian**: Mengelola ketersediaan kamar secara transaksional untuk tanggal tertentu, melindungi _invariant_ bahwa jumlah pesanan tidak melebihi alokasi.

## 🛠️ Teknologi yang Digunakan

- **Bahasa:** Python 3.10+
- **Framework API:** FastAPI
- **Server:** Uvicorn

## 🚀 Cara Menjalankan Proyek

### 1. Prasyarat

Pastikan Anda memiliki Python 3.10 atau yang lebih baru terinstal di sistem Anda.

### 2. Instalasi

1.  Clone repositori ini (atau unduh file `main.py` dan `models.py`).
2.  Buka terminal di folder proyek.
3.  Instal _library_ yang dibutuhkan:
    ```bash
    pip install fastapi "uvicorn[standard]"
    ```

### 3. Menjalankan Server

Jalankan server API menggunakan Uvicorn dari terminal Anda:

```bash
uvicorn main:app --reload
```
