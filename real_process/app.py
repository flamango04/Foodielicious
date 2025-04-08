import os
import time
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, session
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from testing_ingredient import load_ingredient_mapping, convert_ingredients_to_ids, search_recipes_by_ingredient_ids, load_recipe_names, load_recipe_details
from youtubelinks import search_youtube

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")  # Required for session

# === Load Data ===
MAPPING_CSV_PATH = "dataset/ingr_map.csv"
RECIPES_CSV_PATH = "dataset/RAW_recipes.csv"
REVIEW_JSON_PATH = "dataset/recipes_reviews.json"
YOUTUBE_API_KEY = "AIzaSyAaS-mrZjYwML4-ZKH6A18F2sViuvbfWsM"

ingredient_mapping = load_ingredient_mapping(MAPPING_CSV_PATH)
df = pd.read_csv(MAPPING_CSV_PATH)
recipe_names_mapping = load_recipe_names(RECIPES_CSV_PATH)

with open(REVIEW_JSON_PATH) as f:
    all_reviews = json.load(f)

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])
    query = query.lower().strip()
    filtered_df = df[df["processed"].str.contains(query, case=False, na=False)]
    suggestions = sorted(set(filtered_df["processed"].unique()), key=len)[:10]
    return jsonify(list(suggestions))

def get_recipe_data_from_ingredients(ingredients):
    ingredient_ids = convert_ingredients_to_ids(ingredients, ingredient_mapping)
    es = Elasticsearch(
        ["https://localhost:9200"],
        basic_auth=("elastic", "kpsCLdCu6TN5YS5yaYBV"),
        verify_certs=False
    )
    search_results = search_recipes_by_ingredient_ids(es, "ingredient", ingredient_ids, True)
    sorted_results = sorted(search_results, key=lambda r: len(r["_source"]["ingredient_ids"]))
    recipe_data = []
    for r in sorted_results:
        recipe_id = r["_source"]["id"]
        recipe_name = recipe_names_mapping.get(recipe_id, "Name not found")
        recipe_data.append({
            "id": recipe_id,
            "name": recipe_name
        })
    return recipe_data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_ingredients = request.form.get("selected_ingredients", "").strip()
        session["selected_ingredients"] = selected_ingredients
        ingredients = [i.strip() for i in selected_ingredients.split(",") if i.strip()]
        recipe_data = get_recipe_data_from_ingredients(ingredients)

        return render_template("results.html", ingredients=selected_ingredients, recipe_data=recipe_data)

    return render_template("index.html")

@app.route("/results")
def results_page():
    selected_ingredients = session.get("selected_ingredients", "")
    ingredients = [i.strip() for i in selected_ingredients.split(",") if i.strip()]
    recipe_data = get_recipe_data_from_ingredients(ingredients)
    return render_template("results.html", ingredients=selected_ingredients, recipe_data=recipe_data)

@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe_name = recipe_names_mapping.get(recipe_id, "Recipe Not Found")
    minutes, nutrition, steps, description, recipe_ingredients = load_recipe_details(recipe_id, RECIPES_CSV_PATH)
    video_results = search_youtube(f"how to make {recipe_name}", api_key=YOUTUBE_API_KEY)

    review_data = all_reviews.get(str(recipe_id), {})
    ratings = review_data.get("rating", [])
    reviews = review_data.get("review", [])
    ratings_reviews = list(zip(ratings, reviews))
    ingredients = [recipe_ingredients]
    mins = [minutes]
    calories = nutrition[1:]
    calories = [calories.split(",")[0]]
    print("calories: " + str(calories))
    details = list(zip(ingredients, calories, mins))

    return render_template("recipe_detail.html",
                           recipe_name=recipe_name,
                           details=details,
                           steps=steps,
                           description=description,
                           video_results=video_results,
                           ratings_reviews=ratings_reviews)

if __name__ == "__main__":
    app.run(debug=True)
