# OpenSearch Rumah Sakit - ROBD

## Deskripsi

Project ini merupakan implementasi OpenSearch untuk studi kasus Rumah Sakit Sehat Selalu.

OpenSearch digunakan sebagai search engine yang nantinya akan mendukung pengembangan Question Answering (QA) System.

---

## Struktur Folder

```text
OPENSEARCH_RS/
│
├── data/
│   ├── JSON/
│   └── CSV/
│
├── create_all_indexes.py
├── docker-compose.yml
└── README.md
```

---

## Persiapan

### 1. Install Docker Desktop

Download dan install Docker Desktop:

https://www.docker.com/products/docker-desktop/

Pastikan Docker Desktop berjalan sebelum melanjutkan.

---

### 2. Menjalankan OpenSearch

Buka terminal pada folder project:

```bash
docker compose up -d
```

Untuk memastikan OpenSearch berjalan:

```bash
docker ps
```

Buka browser:

```text
http://localhost:9200
```

Jika berhasil akan muncul informasi OpenSearch dalam format JSON.

---

## Membuat Index

Jalankan:

```bash
python create_all_indexes.py
```

Script ini akan membuat index:

* pasien
* dokter
* layanan
* tagihan
* pembayaran
* asuransi
* polis
* departemen
* penanggung_jawab
* tim_medis
* tim_medis_dokter
* detail_tagihan
* bukti_pembayaran

---

## Verifikasi Index

Buka:

```text
http://localhost:9200/_cat/indices?v
```

Pastikan seluruh index berhasil dibuat.

---

## Catatan

Status index kemungkinan akan muncul sebagai:

```text
yellow
```

Hal ini normal karena OpenSearch dijalankan menggunakan konfigurasi single-node.