# Kelompok-3-Jarkom
Nama:

-
-
- Renata Ayu Sekar Kumala (25/557585/PA/23428)
- Ucok Kamal (25/566250/PA/23896)


# Server — Aplikasi Jaringan Socket Programming

Implementasi server sesuai `PROTOCOL.md`. Dibangun dengan Python standard library saja (`socket`, `json`, `random`) — tidak ada dependency eksternal.

## Struktur File

- `server.py` — program utama: socket TCP, loop terima klien, logika request/response/ACK/penonaktifan layanan.
- `protocol.py` — konstanta jenis pesan & kode layanan, fungsi kirim/terima pesan JSON.
- `services.py` — implementasi murni kelima layanan (hitung karakter, hitung kata, reverse string, hapus vokal, determinan & invers matriks 3x3).

## Cara Menjalankan

```bash
python server.py
```

Server bind ke port `12000` dan menunggu koneksi klien.

## Konfigurasi

- `PORT` di `server.py` — port yang dipakai, harus sama dengan yang dipakai klien.
- `WRONG_PROBABILITY` di `server.py` — peluang server sengaja mengirim jawaban salah (default `0.25`).

## Perilaku

- Kelima layanan aktif di awal.
- Setiap request diproses, lalu secara acak hasilnya bisa sengaja dibuat salah.
- Jika klien membalas ACK `INCORRECT`, layanan itu dinonaktifkan permanen dan klien diberi tahu lewat `SERVICE_DISABLED_NOTICE`.
- Jika klien meminta layanan yang sudah nonaktif, server membalas status `SERVICE_DISABLED` tanpa memproses.
- Jika kelima layanan sudah nonaktif semua, server mengirim `SERVER_SHUTDOWN` lalu berhenti (proses keluar).
- Status layanan bersifat global, dibagi ke semua koneksi klien.
