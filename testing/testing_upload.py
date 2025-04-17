#%%
from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=("elastic", "dbsFOxSUAvzyH_K5s6zH"),
    verify_certs=True,
    ca_certs="http_ca.crt",
)

def clean_data(data):
    if "name" in data:
        data["name"] = " ".join(data["name"].split())
    return data

def bulk_upload_to_es(es, bulk_file_path, index_name):
    def generate_actions():
        with open(bulk_file_path, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 2):
                doc_line = lines[i + 1].strip()
                doc = json.loads(doc_line)
                yield {"_index": index_name, "_source": clean_data(doc)}

    helpers.bulk(es, generate_actions())

bulk_file_path = "dataset/RAW_recipes_name_ingredient_bulk.json"
index_name = "recipes"
bulk_upload_to_es(es, bulk_file_path, index_name)

#%%
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ["https://127.0.0.1:9200"],
    basic_auth=("elastic", "dbsFOxSUAvzyH_K5s6zH"),
    verify_certs=True,
    ca_certs="http_ca.crt",
)

def search_recipes_by_ingredients(es, index_name, ingredients, match_all=True):
    if match_all:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"ingredients.keyword": ingredient}}
                        for ingredient in ingredients
                    ]
                }
            }
        }
    else:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"ingredients.keyword": ingredient}}
                        for ingredient in ingredients
                    ],
                    "minimum_should_match": 1
                }
            }
        }

    response = es.search(index=index_name, query=query["query"], size=50)
    
    return response["hits"]["hits"]

if __name__ == "__main__":
    index_name = "recipes"
    ingredients = ["cheese", "beef", "onion"]
    match_all = True  

    recipes = search_recipes_by_ingredients(es, index_name, ingredients, match_all)
    print("Recipes you can make:")

    for recipe in recipes:
        recipe_name = recipe["_source"]["name"]
        recipe_ingredients = recipe["_source"]["ingredients"]
        print(f"- {recipe_name}")
        # print(f"Ingredients: {recipe_ingredients}")

        missing_ingredients = [ing for ing in ingredients if ing not in recipe_ingredients]
        if not missing_ingredients:
            print("All input ingredients are present.")
        else:
            print(f"Missing ingredients: {missing_ingredients}")
# %%
import pandas as pd

# Load the pickle file
data = pd.read_pickle("dataset/ingr_map.pkl")

# Specify the output CSV file path
output_csv_file_path = "ingr_map.csv"

# Check if the data is a DataFrame or needs conversion
if isinstance(data, pd.DataFrame):
    # Write DataFrame to CSV
    data.to_csv(output_csv_file_path, index=False, encoding="utf-8")
else:
    # If data is not a DataFrame, attempt to convert to one
    try:
        df = pd.DataFrame(data)
        df.to_csv(output_csv_file_path, index=False, encoding="utf-8")
    except ValueError as e:
        print(f"Error: Could not convert data to DataFrame. Details: {e}")

print(f"Data has been successfully written to {output_csv_file_path}")


#%%
import pandas as pd

pp_recipes_path = "dataset/PP_recipes.csv"
pp_recipes = pd.read_csv(pp_recipes_path)

pp_recipes["name_tokens"] = pp_recipes["name_tokens"].apply(eval)
pp_recipes["ingredient_ids"] = pp_recipes["ingredient_ids"].apply(eval)

all_name_tokens = set(
    token for tokens_list in pp_recipes["name_tokens"] for token in tokens_list
)
all_ingredient_ids = set(
    token for tokens_list in pp_recipes["ingredient_ids"] for token in tokens_list
)

ingr_map_path = "dataset/ingr_map.csv"
ingr_map = pd.read_csv(ingr_map_path)

ingr_ids = set(ingr_map["id"])

missing_name_tokens = all_name_tokens - ingr_ids
missing_ingredient_ids = all_ingredient_ids - ingr_ids

# print("missing name_tokens:", missing_name_tokens if missing_name_tokens else "nothing")
print("missing ingredient_ids:", missing_ingredient_ids if missing_ingredient_ids else "nothing")


#%%
import pandas as pd

# Load PP_recipes.csv and RAW_recipes.csv
pp_recipes_path = "dataset/PP_recipes.csv"
raw_recipes_path = "dataset/RAW_recipes.csv"

pp_recipes = pd.read_csv(pp_recipes_path)
raw_recipes = pd.read_csv(raw_recipes_path)

# Extract the unique IDs from PP_recipes.csv
pp_ids = set(pp_recipes["id"])

# Filter RAW_recipes.csv to find matching IDs
matching_recipes = raw_recipes[raw_recipes["id"].isin(pp_ids)]

# Check for IDs in PP_recipes.csv that are not found in RAW_recipes.csv
missing_ids = pp_ids - set(raw_recipes["id"])

# Output the results
print("Matching Recipes:")
print(matching_recipes[["id", "name"]])

if missing_ids:
    print("\nIDs in PP_recipes.csv not found in RAW_recipes.csv:")
    print(missing_ids)
else:
    print("\nAll IDs in PP_recipes.csv are found in RAW_recipes.csv.")
