from fastapi import FastAPI
from pydantic import BaseModel
from opensearchpy import OpenSearch

app = FastAPI(
    title="QA System Rumah Sakit Sehat Selalu",
    version="1.0"
)

# Request Model
class Question(BaseModel):
    question: str

# OpenSearch Connection
client = OpenSearch(
    hosts=[{
        "host": "localhost",
        "port": 9200
    }],
    use_ssl=False,
    verify_certs=False
)

# Helper Search
def search_one(index_name, field, value):

    result = client.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    field: value
                }
            }
        }
    )

    hits = result["hits"]["hits"]

    if len(hits) == 0:
        return None

    return hits[0]["_source"]

# Home
@app.get("/")
def home():

    return {
        "message": "QA System Rumah Sakit Sehat Selalu"
    }

# Main QA Endpoint

@app.post("/ask")
def ask(data: Question):

    question = data.question.lower()

    # 1. DOKTER BERDASARKAN SPESIALISASI
    if "dokter" in question and "neurologi" in question:

        result = client.search(
            index="dokter",
            body={
                "query": {
                    "match": {
                        "spesialisasi": "Neurologi"
                    }
                }
            }
        )

        dokter = [
            hit["_source"]["nama_dokter"]
            for hit in result["hits"]["hits"]
        ]

        return {
            "answer":
            f"Dokter spesialis Neurologi: {', '.join(dokter)}"
        }

    if "dokter" in question and "kardiologi" in question:

        result = client.search(
            index="dokter",
            body={
                "query": {
                    "match": {
                        "spesialisasi": "Kardiologi"
                    }
                }
            }
        )

        dokter = [
            hit["_source"]["nama_dokter"]
            for hit in result["hits"]["hits"]
        ]

        return {
            "answer":
            f"Dokter spesialis Kardiologi: {', '.join(dokter)}"
        }

    # 2. DOKTER YANG MENANGANI PASIEN
    if (
        "dokter yang menangani" in question
        or "dokter pasien" in question
    ):

        pasien_result = client.search(
            index="pasien",
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": [
                            "nama_pasien",
                            "id_pasien"
                        ]
                    }
                }
            }
        )

        pasien_hits = pasien_result["hits"]["hits"]

        if len(pasien_hits) == 0:

            return {
                "answer": "Pasien tidak ditemukan"
            }

        pasien = pasien_hits[0]["_source"]

        id_tim = pasien["id_tim"]

        tim_dokter = client.search(
            index="tim_medis_dokter",
            body={
                "query": {
                    "match": {
                        "id_tim": id_tim
                    }
                }
            }
        )

        dokter_list = []

        for item in tim_dokter["hits"]["hits"]:

            id_dokter = item["_source"]["id_dokter"]

            dokter = search_one(
                "dokter",
                "id_dokter",
                id_dokter
            )

            if dokter:
                dokter_list.append(
                    dokter["nama_dokter"]
                )

        return {
            "answer":
            f"Dokter yang menangani {pasien['nama_pasien']} adalah {', '.join(dokter_list)}"
        }

    # 3. PENANGGUNG JAWAB PASIEN
    if "penanggung jawab" in question:

        pasien_result = client.search(
            index="pasien",
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": [
                            "nama_pasien",
                            "id_pasien"
                        ]
                    }
                }
            }
        )

        hits = pasien_result["hits"]["hits"]

        if len(hits) == 0:

            return {
                "answer": "Pasien tidak ditemukan"
            }

        pasien = hits[0]["_source"]

        pj = search_one(
            "penanggung_jawab",
            "id_pasien",
            pasien["id_pasien"]
        )

        if not pj:

            return {
                "answer":
                "Data penanggung jawab tidak ditemukan"
            }

        return {
            "answer":
            f"Penanggung jawab pasien {pasien['nama_pasien']} adalah {pj['nama']} ({pj['hubungan_dengan_pasien']})"
        }

    # 4. TAGIHAN PASIEN
    if "tagihan" in question:

        pasien_result = client.search(
            index="pasien",
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": [
                            "nama_pasien",
                            "id_pasien"
                        ]
                    }
                }
            }
        )

        hits = pasien_result["hits"]["hits"]

        if len(hits) > 0:

            pasien = hits[0]["_source"]

            tagihan = search_one(
                "tagihan",
                "id_pasien",
                pasien["id_pasien"]
            )

            if tagihan:

                return {
                    "answer":
                    f"Total tagihan pasien {pasien['nama_pasien']} adalah Rp {tagihan['total_biaya']:,} dengan status {tagihan['status_bayar']}"
                }

    # 5. ASURANSI PASIEN
    if "asuransi" in question:

        pasien_result = client.search(
            index="pasien",
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": [
                            "nama_pasien",
                            "id_pasien"
                        ]
                    }
                }
            }
        )

        hits = pasien_result["hits"]["hits"]

        if len(hits) > 0:

            pasien = hits[0]["_source"]

            polis = search_one(
                "polis",
                "id_pasien",
                pasien["id_pasien"]
            )

            if polis:

                asuransi = search_one(
                    "asuransi",
                    "id_asuransi",
                    polis["id_asuransi"]
                )

                if asuransi:

                    return {
                        "answer":
                        f"Asuransi pasien {pasien['nama_pasien']} adalah {asuransi['nama_asuransi']}"
                    }

    # 6. STATUS POLIS
    if "polis" in question:

        pasien_result = client.search(
            index="pasien",
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": [
                            "nama_pasien",
                            "id_pasien"
                        ]
                    }
                }
            }
        )

        hits = pasien_result["hits"]["hits"]

        if len(hits) > 0:

            pasien = hits[0]["_source"]

            polis = search_one(
                "polis",
                "id_pasien",
                pasien["id_pasien"]
            )

            if polis:

                return {
                    "answer":
                    f"Status polis pasien {pasien['nama_pasien']} adalah {polis['status_polis']}"
                }

    # 7. TIM MEDIS
    if "tim medis" in question:

        pasien_result = client.search(
            index="pasien",
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": [
                            "nama_pasien",
                            "id_pasien"
                        ]
                    }
                }
            }
        )

        hits = pasien_result["hits"]["hits"]

        if len(hits) > 0:

            pasien = hits[0]["_source"]

            tim = search_one(
                "tim_medis",
                "id_tim",
                pasien["id_tim"]
            )

            if tim:

                return {
                    "answer":
                    f"Pasien {pasien['nama_pasien']} berada pada {tim['nama_tim']}"
                }

    # FALLBACK SEARCH
    indexes = [
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

    for idx in indexes:

        result = client.search(
            index=idx,
            body={
                "query": {
                    "multi_match": {
                        "query": data.question,
                        "fields": ["*"]
                    }
                }
            }
        )

        hits = result["hits"]["hits"]

        if len(hits) > 0:

            return {
                "index": idx,
                "answer": hits[0]["_source"]
            }

    return {
        "answer": "Data tidak ditemukan"
    }