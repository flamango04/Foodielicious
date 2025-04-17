#%%
import csv
from elasticsearch import Elasticsearch

import os
print(os.getcwd()) 

#%%
es = Elasticsearch(
    ["https://localhost:9200"], 
    basic_auth=("elastic", "dbsFOxSUAvzyH_K5s6zH"), 
    verify_certs=False
)
# es = Elasticsearch(
#     ["https://localhost.248:9200"],
#     basic_auth=("elastic", "27NqMNCgHBol_n*j0XDv"),
#     verify_certs=False
# )

csv_file_path = "../dataset/ingr_map.csv"

def load_ingredient_mapping(csv_file_path):
    ingredient_to_id = {}
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            raw_ingr = row["raw_ingr"].strip().lower()
            ingredient_id = int(row["id"])
            ingredient_to_id[raw_ingr] = ingredient_id
    return ingredient_to_id

def convert_ingredients_to_ids(ingredients, ingredient_mapping):
    ids = []
    for ingredient in ingredients:
        normalized_ingredient = ingredient.strip().lower()
        if normalized_ingredient in ingredient_mapping:
            ids.append(ingredient_mapping[normalized_ingredient])
        else:
            print(f"Ingredient '{ingredient}' not found in the mapping.")
    return ids

def load_recipe_details(id, csv_file_path):
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if id == int(row["id"]):
                minutes = row["minutes"]
                nutrition = row["nutrition"]
                steps = row["steps"]
                description = row["description"]
                recipe_ingredients = row["ingredients"]

    return minutes, nutrition, steps, description, recipe_ingredients

def search_recipes_by_ingredient_ids(es, index_name, ingredient_ids, match_all=True):
    if not ingredient_ids:
        return []
    if match_all:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"ingredient_ids": ingredient_id}}
                        for ingredient_id in ingredient_ids
                    ]
                }
            }
        }
    else:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"ingredient_ids": ingredient_id}}
                        for ingredient_id in ingredient_ids
                    ],
                    "minimum_should_match": 1
                }
            }
        }

    response = es.search(index=index_name, query=query["query"], size=10)
    return response["hits"]["hits"]

def load_recipe_names(csv_file_path):
    recipe_names = {}
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            recipe_id = int(row["id"])  
            recipe_name = row["name"]  
            recipe_names[recipe_id] = recipe_name
    return recipe_names

#%%
if __name__ == "__main__":
    ingredient_mapping = load_ingredient_mapping(csv_file_path)

    input_ingredients = []

    ingredient_ids = convert_ingredients_to_ids(input_ingredients, ingredient_mapping)
    print(f"Ingredient IDs: {ingredient_ids}")

    index_name = "ingredient"
    match_all = True
    search_results = search_recipes_by_ingredient_ids(es, index_name, ingredient_ids, match_all)

    raw_recipes_csv_path = "../dataset/RAW_recipes.csv"
    recipe_names_mapping = load_recipe_names(raw_recipes_csv_path)

    sorted_results = sorted(
        search_results,
        key=lambda result: len(result["_source"]["ingredient_ids"])  
    )

    print("Search Results (Sorted by Ingredient Count):")
    for result in sorted_results:
        recipe_id = result["_source"]["id"]
        recipe_name = recipe_names_mapping.get(recipe_id, "Name not found in CSV")
        ingredient_count = len(result["_source"]["ingredient_ids"])  
        print(f"Recipe ID: {recipe_id}, Name: {recipe_name}, Ingredient Count: {ingredient_count}")

# %%