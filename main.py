import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from opensearchpy import OpenSearch

app = FastAPI(
    title="QA System Rumah Sakit Sehat Selalu",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

client = OpenSearch(
    hosts=[{
        "host": "localhost",
        "port": 9200
    }],
    use_ssl=False,
    verify_certs=False
)

ENTITY_CONFIG = {
    "pasien": {
        "id_field": "id_pasien",
        "name_fields": ["nama_pasien"]
    },
    "dokter": {
        "id_field": "id_dokter",
        "name_fields": ["nama_dokter", "spesialisasi"]
    },
    "layanan": {
        "id_field": "id_layanan",
        "name_fields": ["nama_layanan", "jenis_layanan"]
    },
    "tagihan": {
        "id_field": "id_tagihan",
        "name_fields": ["id_pasien", "metode_pembayaran", "status_bayar"]
    },
    "pembayaran": {
        "id_field": "id_pembayaran",
        "name_fields": ["id_tagihan", "metode_bayar", "status_bayar"]
    },
    "asuransi": {
        "id_field": "id_asuransi",
        "name_fields": ["nama_asuransi"]
    },
    "polis": {
        "id_field": "id_polis",
        "name_fields": ["nomor_polis", "status_polis", "id_pasien", "id_asuransi"]
    },
    "departemen": {
        "id_field": "id_departemen",
        "name_fields": ["nama_departemen"]
    },
    "penanggung_jawab": {
        "id_field": "id_penanggung_jawab",
        "name_fields": ["nama", "hubungan_dengan_pasien", "id_pasien"]
    },
    "tim_medis": {
        "id_field": "id_tim",
        "name_fields": ["nama_tim"]
    },
    "tim_medis_dokter": {
        "id_field": "id_tim",
        "name_fields": ["id_tim", "id_dokter"]
    },
    "detail_tagihan": {
        "id_field": "id_detail_tagihan",
        "name_fields": ["id_tagihan", "id_layanan", "status_cover"]
    },
    "bukti_pembayaran": {
        "id_field": "id_bukti",
        "name_fields": ["id_pembayaran", "tanggal_bukti"]
    }
}

ID_PATTERNS = [
    ("detail_tagihan", r"\bDT\d{3}\b"),
    ("tagihan", r"\bTGH\d{3}\b"),
    ("pembayaran", r"\bBYR\d{3}\b"),
    ("bukti_pembayaran", r"\bBK\d{3}\b"),
    ("departemen", r"\bDEP\d{3}\b"),
    ("penanggung_jawab", r"\bPJ\d{3}\b"),
    ("polis", r"\bPL\d{3}\b"),
    ("pasien", r"\bP\d{3}\b"),
    ("dokter", r"\bD\d{3}\b"),
    ("layanan", r"\bL\d{3}\b"),
    ("asuransi", r"\bA\d{3}\b"),
    ("tim_medis", r"\bT\d{3}\b"),
]

INDEXES = [
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


def rupiah(value):
    try:
        return "Rp " + f"{int(value):,}".replace(",", ".")
    except:
        return str(value)


def search_one(index_name, field, value):
    result = client.search(
        index=index_name,
        body={
            "size": 1,
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


def search_many(index_name, field, value, size=50):
    result = client.search(
        index=index_name,
        body={
            "size": size,
            "query": {
                "match": {
                    field: value
                }
            }
        }
    )

    return [hit["_source"] for hit in result["hits"]["hits"]]


def search_text(index_name, text, fields=None, size=5):
    if not fields:
        fields = ["*"]

    result = client.search(
        index=index_name,
        body={
            "size": size,
            "query": {
                "multi_match": {
                    "query": text,
                    "fields": fields
                }
            }
        }
    )

    return [hit["_source"] for hit in result["hits"]["hits"]]


def extract_entity_id(question_text, target_entity=None):
    question_upper = question_text.upper()

    for entity, pattern in ID_PATTERNS:
        if target_entity and entity != target_entity:
            continue

        match = re.search(pattern, question_upper)

        if match:
            return entity, match.group(0)

    return None, None


def detect_entity_from_question(question_text):
    q = question_text.lower()

    keyword_map = [
        ("detail_tagihan", ["detail tagihan", "detail_tagihan"]),
        ("bukti_pembayaran", ["bukti pembayaran", "bukti_pembayaran", "bukti"]),
        ("penanggung_jawab", ["penanggung jawab", "penanggung_jawab"]),
        ("tim_medis_dokter", ["tim medis dokter", "tim_medis_dokter"]),
        ("tim_medis", ["tim medis", "tim_medis"]),
        ("pembayaran", ["pembayaran", "bayar"]),
        ("departemen", ["departemen"]),
        ("asuransi", ["asuransi"]),
        ("tagihan", ["tagihan", "biaya"]),
        ("layanan", ["layanan"]),
        ("dokter", ["dokter"]),
        ("pasien", ["pasien"]),
        ("polis", ["polis"]),
    ]

    for entity, keywords in keyword_map:
        for keyword in keywords:
            if keyword in q:
                return entity

    return None


def find_entity(index_name, question_text):
    config = ENTITY_CONFIG[index_name]
    id_field = config["id_field"]

    entity, found_id = extract_entity_id(question_text, index_name)

    if found_id:
        doc = search_one(index_name, id_field, found_id)
        if doc:
            return doc

    fields = [id_field] + config["name_fields"]
    results = search_text(index_name, question_text, fields=fields, size=1)

    if len(results) == 0:
        return None

    return results[0]


def find_pasien(question_text):
    return find_entity("pasien", question_text)


def format_doc(index_name, doc):
    if not doc:
        return "Data tidak ditemukan."

    if index_name == "pasien":
        return (
            f"Pasien {doc.get('nama_pasien')} memiliki ID {doc.get('id_pasien')}, "
            f"jenis pasien {doc.get('jenis_pasien')}, pembayaran awal {doc.get('pembayaran_awal')}, "
            f"ID tim {doc.get('id_tim')}, ID polis {doc.get('id_polis') or '-'}, "
            f"dan ID tagihan {doc.get('id_tagihan')}."
        )

    if index_name == "dokter":
        return (
            f"Dokter dengan ID {doc.get('id_dokter')} adalah {doc.get('nama_dokter')}, "
            f"spesialisasi {doc.get('spesialisasi')}, dan berada pada departemen {doc.get('id_departemen')}."
        )

    if index_name == "layanan":
        return (
            f"Layanan dengan ID {doc.get('id_layanan')} adalah {doc.get('nama_layanan')} "
            f"dengan jenis layanan {doc.get('jenis_layanan')}."
        )

    if index_name == "tagihan":
        return (
            f"Tagihan {doc.get('id_tagihan')} untuk pasien {doc.get('id_pasien')} "
            f"memiliki total biaya {rupiah(doc.get('total_biaya'))}, "
            f"metode pembayaran {doc.get('metode_pembayaran')}, "
            f"dan status bayar {doc.get('status_bayar')}."
        )

    if index_name == "pembayaran":
        return (
            f"Pembayaran {doc.get('id_pembayaran')} untuk tagihan {doc.get('id_tagihan')} "
            f"dilakukan dengan metode {doc.get('metode_bayar')}, "
            f"jumlah bayar {rupiah(doc.get('jumlah_bayar'))}, "
            f"dan status {doc.get('status_bayar')}."
        )

    if index_name == "asuransi":
        return (
            f"Asuransi dengan ID {doc.get('id_asuransi')} adalah {doc.get('nama_asuransi')}."
        )

    if index_name == "polis":
        return (
            f"Polis {doc.get('id_polis')} memiliki nomor polis {doc.get('nomor_polis')}, "
            f"status {doc.get('status_polis')}, terhubung dengan pasien {doc.get('id_pasien')} "
            f"dan asuransi {doc.get('id_asuransi')}."
        )

    if index_name == "departemen":
        return (
            f"Departemen dengan ID {doc.get('id_departemen')} adalah {doc.get('nama_departemen')}."
        )

    if index_name == "penanggung_jawab":
        return (
            f"Penanggung jawab dengan ID {doc.get('id_penanggung_jawab')} adalah {doc.get('nama')} "
            f"dengan hubungan {doc.get('hubungan_dengan_pasien')} untuk pasien {doc.get('id_pasien')}."
        )

    if index_name == "tim_medis":
        return (
            f"Tim medis dengan ID {doc.get('id_tim')} adalah {doc.get('nama_tim')}."
        )

    if index_name == "tim_medis_dokter":
        return (
            f"Tim medis {doc.get('id_tim')} memiliki dokter dengan ID {doc.get('id_dokter')}."
        )

    if index_name == "detail_tagihan":
        return (
            f"Detail tagihan {doc.get('id_detail_tagihan')} terhubung dengan tagihan {doc.get('id_tagihan')} "
            f"dan layanan {doc.get('id_layanan')}. Subtotalnya {rupiah(doc.get('subtotal'))}, "
            f"status cover {doc.get('status_cover')}, nominal cover {rupiah(doc.get('nominal_cover'))}, "
            f"dan nominal mandiri {rupiah(doc.get('nominal_mandiri'))}."
        )

    if index_name == "bukti_pembayaran":
        return (
            f"Bukti pembayaran {doc.get('id_bukti')} terhubung dengan pembayaran {doc.get('id_pembayaran')} "
            f"pada tanggal {doc.get('tanggal_bukti')}."
        )

    return str(doc)


def answer_doctors_by_specialization(specialization):
    result = client.search(
        index="dokter",
        body={
            "size": 100,
            "query": {
                "match": {
                    "spesialisasi": specialization
                }
            }
        }
    )

    doctors = [
        hit["_source"]["nama_dokter"]
        for hit in result["hits"]["hits"]
    ]

    if len(doctors) == 0:
        return f"Dokter spesialis {specialization} tidak ditemukan."

    return f"Dokter spesialis {specialization}: {', '.join(doctors)}"


def answer_doctors_for_patient(pasien):
    tim_dokter = search_many(
        "tim_medis_dokter",
        "id_tim",
        pasien["id_tim"],
        size=50
    )

    dokter_list = []

    for item in tim_dokter:
        dokter = search_one(
            "dokter",
            "id_dokter",
            item["id_dokter"]
        )

        if dokter:
            dokter_list.append(dokter["nama_dokter"])

    if len(dokter_list) == 0:
        return f"Data dokter untuk pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Dokter yang menangani pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) adalah {', '.join(dokter_list)}."
    )


def answer_penanggung_jawab(pasien):
    pj = search_one(
        "penanggung_jawab",
        "id_pasien",
        pasien["id_pasien"]
    )

    if not pj and pasien.get("id_penanggung_jawab"):
        pj = search_one(
            "penanggung_jawab",
            "id_penanggung_jawab",
            pasien["id_penanggung_jawab"]
        )

    if not pj:
        return f"Data penanggung jawab pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Penanggung jawab pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) adalah {pj['nama']} "
        f"({pj['hubungan_dengan_pasien']})."
    )


def answer_tagihan(pasien):
    tagihan = search_one(
        "tagihan",
        "id_pasien",
        pasien["id_pasien"]
    )

    if not tagihan and pasien.get("id_tagihan"):
        tagihan = search_one(
            "tagihan",
            "id_tagihan",
            pasien["id_tagihan"]
        )

    if not tagihan:
        return f"Data tagihan pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Total tagihan pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) adalah {rupiah(tagihan['total_biaya'])} "
        f"dengan metode pembayaran {tagihan['metode_pembayaran']} "
        f"dan status {tagihan['status_bayar']}."
    )


def answer_asuransi(pasien):
    polis = search_one(
        "polis",
        "id_pasien",
        pasien["id_pasien"]
    )

    if not polis and pasien.get("id_polis"):
        polis = search_one(
            "polis",
            "id_polis",
            pasien["id_polis"]
        )

    if not polis:
        return f"Data polis pasien {pasien['nama_pasien']} tidak ditemukan."

    asuransi = search_one(
        "asuransi",
        "id_asuransi",
        polis["id_asuransi"]
    )

    if not asuransi:
        return f"Data asuransi pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Asuransi pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) adalah {asuransi['nama_asuransi']} "
        f"dengan nomor polis {polis['nomor_polis']} dan status polis {polis['status_polis']}."
    )


def answer_polis(pasien):
    polis = search_one(
        "polis",
        "id_pasien",
        pasien["id_pasien"]
    )

    if not polis and pasien.get("id_polis"):
        polis = search_one(
            "polis",
            "id_polis",
            pasien["id_polis"]
        )

    if not polis:
        return f"Data polis pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Status polis pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) adalah {polis['status_polis']} "
        f"dengan nomor polis {polis['nomor_polis']}."
    )


def answer_tim_medis(pasien):
    tim = search_one(
        "tim_medis",
        "id_tim",
        pasien["id_tim"]
    )

    if not tim:
        return f"Data tim medis pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) berada pada {tim['nama_tim']}."
    )


def answer_pembayaran(pasien):
    tagihan = search_one(
        "tagihan",
        "id_pasien",
        pasien["id_pasien"]
    )

    if not tagihan and pasien.get("id_tagihan"):
        tagihan = search_one(
            "tagihan",
            "id_tagihan",
            pasien["id_tagihan"]
        )

    if not tagihan:
        return f"Data tagihan pasien {pasien['nama_pasien']} tidak ditemukan."

    pembayaran = search_one(
        "pembayaran",
        "id_tagihan",
        tagihan["id_tagihan"]
    )

    if not pembayaran:
        return f"Data pembayaran pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Pembayaran pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) dilakukan dengan metode {pembayaran['metode_bayar']}, "
        f"jumlah bayar {rupiah(pembayaran['jumlah_bayar'])}, "
        f"dan status pembayaran {pembayaran['status_bayar']}."
    )


def answer_layanan_pasien(pasien):
    tagihan_id = pasien.get("id_tagihan")

    if not tagihan_id:
        tagihan = search_one("tagihan", "id_pasien", pasien["id_pasien"])
        if tagihan:
            tagihan_id = tagihan["id_tagihan"]

    if not tagihan_id:
        return f"Data tagihan pasien {pasien['nama_pasien']} tidak ditemukan."

    detail_list = search_many(
        "detail_tagihan",
        "id_tagihan",
        tagihan_id,
        size=50
    )

    if len(detail_list) == 0:
        return f"Detail layanan pasien {pasien['nama_pasien']} tidak ditemukan."

    layanan_names = []

    for detail in detail_list:
        layanan = search_one(
            "layanan",
            "id_layanan",
            detail["id_layanan"]
        )

        if layanan:
            layanan_names.append(layanan["nama_layanan"])

    if len(layanan_names) == 0:
        return f"Data layanan pasien {pasien['nama_pasien']} tidak ditemukan."

    return (
        f"Layanan untuk pasien {pasien['nama_pasien']} "
        f"({pasien['id_pasien']}) adalah {', '.join(layanan_names)}."
    )


@app.get("/")
def home():
    return {
        "message": "QA System Rumah Sakit Sehat Selalu"
    }


@app.post("/ask")
def ask(data: Question):
    question_text = data.question.strip()
    question = question_text.lower()

    if not question_text:
        return {
            "answer": "Silakan masukkan pertanyaan terlebih dahulu."
        }

    # 1. Dokter berdasarkan spesialisasi
    if "dokter" in question and "neurologi" in question:
        return {
            "answer": answer_doctors_by_specialization("Neurologi")
        }

    if "dokter" in question and "kardiologi" in question:
        return {
            "answer": answer_doctors_by_specialization("Kardiologi")
        }

    # 2. Relasi berbasis pasien: bisa pakai ID pasien atau nama pasien
    is_patient_context = (
        "pasien" in question
        or extract_entity_id(question_text, "pasien")[1] is not None
    )

    if is_patient_context:
        pasien = find_pasien(question_text)

        if not pasien:
            return {
                "answer": "Pasien tidak ditemukan."
            }

        if "dokter" in question and ("menangani" in question or "dokter pasien" in question):
            return {
                "answer": answer_doctors_for_patient(pasien)
            }

        if "penanggung jawab" in question:
            return {
                "answer": answer_penanggung_jawab(pasien)
            }

        if "tagihan" in question or "biaya" in question:
            return {
                "answer": answer_tagihan(pasien)
            }

        if "asuransi" in question:
            return {
                "answer": answer_asuransi(pasien)
            }

        if "polis" in question:
            return {
                "answer": answer_polis(pasien)
            }

        if "tim medis" in question:
            return {
                "answer": answer_tim_medis(pasien)
            }

        if "pembayaran" in question or "bayar" in question:
            return {
                "answer": answer_pembayaran(pasien)
            }

        if "layanan" in question:
            return {
                "answer": answer_layanan_pasien(pasien)
            }

        return {
            "answer": format_doc("pasien", pasien)
        }

    # 3. General search by ID: bisa cari A001, D001, TGH001, BYR001, dan lain-lain
    entity, found_id = extract_entity_id(question_text)

    if entity and found_id:
        id_field = ENTITY_CONFIG[entity]["id_field"]
        doc = search_one(entity, id_field, found_id)

        if doc:
            return {
                "answer": format_doc(entity, doc)
            }

    # 4. General search by entity name
    requested_entity = detect_entity_from_question(question_text)

    if requested_entity:
        doc = find_entity(requested_entity, question_text)

        if doc:
            return {
                "answer": format_doc(requested_entity, doc)
            }

    # 5. Fallback search ke semua index
    for index_name in INDEXES:
        results = search_text(index_name, question_text, fields=["*"], size=1)

        if len(results) > 0:
            return {
                "answer": format_doc(index_name, results[0])
            }

    return {
        "answer": "Data tidak ditemukan."
    }
