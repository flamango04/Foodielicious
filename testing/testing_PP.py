#%%
from elasticsearch import Elasticsearch
import json
from tqdm import tqdm

es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=("elastic", "dbsFOxSUAvzyH_K5s6zH"),
    verify_certs=True,
    ca_certs="http_ca.crt",  
)
with open("PP_recipes.json", "r") as file:
    data = [json.loads(line) for line in file if line.strip()]

chunk_size = 1000  
for i in tqdm(range(0, len(data), chunk_size), desc="Uploading chunks"):
    chunk = data[i:i + chunk_size]
    bulk_data = "\n".join([json.dumps(item) for item in chunk]) + "\n"
    response = es.bulk(body=bulk_data)



#%%
import csv

input_csv_file_path = "dataset/RAW_recipes.csv"
output_csv_file_path = "dataset/RAW_recipes_name_ingredient.csv"

recipe_names = []
ingredients_list = []

with open(input_csv_file_path, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)  
    for row in reader:
        recipe_name = row.get("name")  
        ingredients = row.get("ingredients") 

        if recipe_name and ingredients:
            recipe_names.append(recipe_name)
            ingredients_list.append(ingredients)

with open(output_csv_file_path, mode="w", encoding="utf-8", newline="") as outfile:
    writer = csv.writer(outfile)

    writer.writerow(["name", "ingredients"])

    for name, ingredients in zip(recipe_names, ingredients_list):
        writer.writerow([name, ingredients])

print(f"Data written to {output_csv_file_path}")
