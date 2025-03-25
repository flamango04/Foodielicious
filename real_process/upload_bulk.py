#%%
from elasticsearch import Elasticsearch, helpers
import json

# Elasticsearch connection configuration
es = Elasticsearch(
    ["https://localhost:9200"], 
    basic_auth=("elastic", "zvAznSMH1c10Fn2QXd4H"), 
    verify_certs=False,
)

def bulk_upload_to_es(es, bulk_file_path, index_name):
    def generate_actions():
        with open(bulk_file_path, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 2):
                index_line = json.loads(lines[i].strip())
                doc_line = json.loads(lines[i + 1].strip())
                yield {
                    "_index": index_name,
                    "_id": index_line["index"]["_id"],
                    "_source": doc_line,
                }

    helpers.bulk(es, generate_actions())

bulk_file_path = "../dataset/elastic_bulk_recipes.json"
index_name = "ingredient"

bulk_upload_to_es(es, bulk_file_path, index_name)

print(f"Bulk data successfully uploaded to index {index_name}")

# %%
