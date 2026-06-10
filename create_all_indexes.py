from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{
        "host": "localhost",
        "port": 9200
    }],
    use_ssl=False,
    verify_certs=False
)

indexes = {

    "pasien": {
        "properties": {
            "id_pasien": {"type": "keyword"},
            "nama_pasien": {"type": "text"},
            "jenis_pasien": {"type": "keyword"},
            "id_penanggung_jawab": {"type": "keyword"},
            "id_tim": {"type": "keyword"},
            "pembayaran_awal": {"type": "keyword"},
            "id_polis": {"type": "keyword"},
            "id_tagihan": {"type": "keyword"}
        }
    },

    "dokter": {
        "properties": {
            "id_dokter": {"type": "keyword"},
            "nama_dokter": {"type": "text"},
            "spesialisasi": {"type": "keyword"},
            "id_departemen": {"type": "keyword"}
        }
    },

    "layanan": {
        "properties": {
            "id_layanan": {"type": "keyword"},
            "nama_layanan": {"type": "text"},
            "jenis_layanan": {"type": "keyword"}
        }
    },

    "tagihan": {
        "properties": {
            "id_tagihan": {"type": "keyword"},
            "id_pasien": {"type": "keyword"},
            "metode_pembayaran": {"type": "keyword"},
            "total_biaya": {"type": "long"},
            "status_bayar": {"type": "keyword"}
        }
    },

    "pembayaran": {
        "properties": {
            "id_pembayaran": {"type": "keyword"},
            "id_tagihan": {"type": "keyword"},
            "metode_bayar": {"type": "keyword"},
            "jumlah_bayar": {"type": "long"},
            "status_bayar": {"type": "keyword"}
        }
    },

    "asuransi": {
        "properties": {
            "id_asuransi": {"type": "keyword"},
            "nama_asuransi": {"type": "text"}
        }
    },

    "polis": {
        "properties": {
            "id_polis": {"type": "keyword"},
            "nomor_polis": {"type": "keyword"},
            "status_polis": {"type": "keyword"},
            "id_pasien": {"type": "keyword"},
            "id_asuransi": {"type": "keyword"}
        }
    },

    "departemen": {
        "properties": {
            "id_departemen": {"type": "keyword"},
            "nama_departemen": {"type": "text"}
        }
    },

    "penanggung_jawab": {
        "properties": {
            "id_penanggung_jawab": {"type": "keyword"},
            "nama": {"type": "text"},
            "hubungan_dengan_pasien": {"type": "keyword"},
            "id_pasien": {"type": "keyword"}
        }
    },

    "tim_medis": {
        "properties": {
            "id_tim": {"type": "keyword"},
            "nama_tim": {"type": "text"}
        }
    },

    "tim_medis_dokter": {
        "properties": {
            "id_tim": {"type": "keyword"},
            "id_dokter": {"type": "keyword"}
        }
    },

    "detail_tagihan": {
        "properties": {
            "id_detail_tagihan": {"type": "keyword"},
            "id_tagihan": {"type": "keyword"},
            "id_layanan": {"type": "keyword"},
            "subtotal": {"type": "long"},
            "status_cover": {"type": "keyword"},
            "nominal_cover": {"type": "long"},
            "nominal_mandiri": {"type": "long"}
        }
    },

    "bukti_pembayaran": {
        "properties": {
            "id_bukti": {"type": "keyword"},
            "id_pembayaran": {"type": "keyword"},
            "tanggal_bukti": {"type": "date"}
        }
    }
}

for index_name, mapping in indexes.items():

    client.indices.create(
        index=index_name,
        body={"mappings": mapping},
        ignore=400
    )

    print(f"{index_name} berhasil dibuat")

print("\nSemua index berhasil dibuat")