Master data Rumah Sakit Sehat Selalu
Semua file dibuat agar bisa dipakai bareng oleh tiap anggota.
Format tersedia dalam JSON dan CSV per entitas.

Daftar file:
- departemen
- dokter
- tim_medis
- tim_medis_dokter
- pasien
- penanggung_jawab
- asuransi
- polis
- layanan
- tagihan
- detail_tagihan
- pembayaran
- bukti_pembayaran

Saran penggunaan:
- Anggota Document DB: pakai file-file ini sebagai data master, lalu embed jadi document nested.
- Anggota Relational DB: import CSV ke tabel sesuai entitas.
- Anggota Graph DB: jadikan node dan relationship berdasarkan ID.
- Anggota Column DB: gunakan CSV sebagai sumber import tabel.
