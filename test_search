from opensearchpy import OpenSearch
import json

client = OpenSearch(
    hosts=[{
        "host": "localhost",
        "port": 9200
    }],
    use_ssl=False,
    verify_certs=False
)

result = client.search(
    index="dokter",
    body={
        "query": {
            "match_all": {}
        }
    }
)

print("Jumlah hasil:",
      result["hits"]["total"]["value"])

for hit in result["hits"]["hits"][:5]:
    print(json.dumps(
        hit["_source"],
        indent=2,
        ensure_ascii=False
    ))
