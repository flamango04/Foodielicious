import os
from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from testing_ingredient import load_ingredient_mapping, convert_ingredients_to_ids, search_recipes_by_ingredient_ids, load_recipe_names
from dotenv import load_dotenv
import pandas as pd
from youtubelinks import search_youtube

load_dotenv()

app = Flask(__name__)

MAPPING_CSV_PATH = "../dataset/ingr_map.csv"
RECIPES_CSV_PATH = "../dataset/RAW_recipes.csv"

df = pd.read_csv(MAPPING_CSV_PATH)

def get_recipes_from_ingredients(ingredients):
    if not ingredients:
        return [] 

    ingredient_mapping = load_ingredient_mapping(MAPPING_CSV_PATH)
    ingredient_ids = convert_ingredients_to_ids(ingredients, ingredient_mapping)

    es = Elasticsearch(
        ["https://localhost:9200"], 
        basic_auth=("elastic", "TY3LPHF1VTD4j-dODgyu"), 
        verify_certs=False,
        ssl_show_warn=False,
    )

    index_name = "ingredient"
    match_all = True
    search_results = search_recipes_by_ingredient_ids(es, index_name, ingredient_ids, match_all)

    recipe_names_mapping = load_recipe_names(RECIPES_CSV_PATH)
    sorted_results = sorted(
        search_results,
        key=lambda result: len(result["_source"]["ingredient_ids"])
    )

    recipes = []
    for result in sorted_results:
        recipe_id = result["_source"]["id"]
        recipe_name = recipe_names_mapping.get(recipe_id, "Name not found")
        recipes.append(recipe_name)
    
    print("Recipes found:", recipes)
    return recipes

def find_related_ingredients(query):
    query = query.lower().strip()
    filtered_df = df[df["processed"].str.contains(query, case=False, na=False)]
    suggestions = filtered_df["processed"].unique()[:10]
    return list(suggestions)

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])
    
    return jsonify(find_related_ingredients(query))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_ingredients = request.form.get("selected_ingredients", "").strip()
        ingredients = [i.strip() for i in selected_ingredients.split(",") if i.strip()]
        
        recipes = get_recipes_from_ingredients(ingredients)

        api_key = "AIzaSyAaS-mrZjYwML4-ZKH6A18F2sViuvbfWsM"
        recipe_data = []
        for recipe in recipes:
            query = f"how to make {recipe}"
            video_results = search_youtube(query, api_key)  
            recipe_data.append({
                "name": recipe,
                "videos": video_results  
            })

        print("Final recipe data:", recipe_data) 

        return render_template("results.html", ingredients=selected_ingredients, recipe_data=recipe_data)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
