import json
import os
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{
        "host": "localhost",
        "port": 9200
    }],
    use_ssl=False,
    verify_certs=False
)

DATA_FOLDER = "data/JSON"

files = [
    "pasien",
    "dokter",
    "layanan",
    "tagihan",
    "pembayaran",
    "asuransi",
    "polis",
    "departemen",
    "penanggung_jawab",
    "tim_medis",
    "tim_medis_dokter",
    "detail_tagihan",
    "bukti_pembayaran"
]

for index_name in files:

    file_path = os.path.join(
        DATA_FOLDER,
        f"{index_name}.json"
    )

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for doc in data:
        client.index(
            index=index_name,
            body=doc
        )

    print(
        f"{len(data)} data berhasil dimasukkan ke index {index_name}"
    )

print("\nSemua data berhasil dimasukkan ke OpenSearch")
