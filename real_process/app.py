import os
import time
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from testing_ingredient import load_ingredient_mapping, convert_ingredients_to_ids, search_recipes_by_ingredient_ids, load_recipe_names
from youtubelinks import search_youtube

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

# === File Paths ===
MAPPING_CSV_PATH = "../dataset/ingr_map.csv"
RECIPES_CSV_PATH = "../dataset/RAW_recipes.csv"
REVIEW_JSON_PATH = "../dataset/recipes_reviews.json"
USER_DATA_PATH = "data/users.json"
YOUTUBE_API_KEY = "AIzaSyAaS-mrZjYwML4-ZKH6A18F2sViuvbfWsM"

# === Load Data ===
ingredient_mapping = load_ingredient_mapping(MAPPING_CSV_PATH)
df = pd.read_csv(MAPPING_CSV_PATH)
recipe_names_mapping = load_recipe_names(RECIPES_CSV_PATH)
with open(REVIEW_JSON_PATH) as f:
    all_reviews = json.load(f)

def load_users():
    if not os.path.exists(USER_DATA_PATH):
        return {}
    with open(USER_DATA_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_PATH, "w") as f:
        json.dump(users, f, indent=2)

@app.context_processor
def inject_user():
    return dict(logged_in=session.get("username"), current_user=session.get("username"))

@app.route("/register", methods=["GET", "POST"])
def register():
    error = {}
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()

        if username in users:
            error["username"] = "Username already exists. Want to login?"
        elif not username or not password:
            error["username"] = "Username and password are required."

        if not error:
            users[username] = {
                "password": password,
                "search_history": [],
                "viewed_recipes": []
            }
            save_users(users)
            session["username"] = username
            return redirect(url_for("index"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = {}
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()

        if username not in users:
            error["username"] = "Invalid username. Want to register?"
        elif users[username]["password"] != password:
            error["password"] = "Incorrect password."

        if not error:
            session["username"] = username
            return redirect(url_for("index"))

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

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
        basic_auth=("elastic", "zvAznSMH1c10Fn2QXd4H"),
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

        # Save user search history
        if "username" in session:
            users = load_users()
            username = session["username"]
            users[username]["search_history"].append(selected_ingredients)
            save_users(users)

        return render_template("results.html", ingredients=selected_ingredients, recipe_data=recipe_data)

    return render_template("index.html")

@app.route("/results")
def results_page():
    selected_ingredients = session.get("selected_ingredients", "")
    ingredients = [i.strip() for i in selected_ingredients.split(",") if i.strip()]
    recipe_data = get_recipe_data_from_ingredients(ingredients)

    user_history = []
    if "username" in session:
        users = load_users()
        user_history = users.get(session["username"], {}).get("search_history", [])

    return render_template("results.html", ingredients=selected_ingredients, recipe_data=recipe_data, user_history=user_history)

@app.route("/validate_ingredient", methods=["GET"])
def validate_ingredient():
    ingredient = request.args.get("ingredient", "").lower().strip()
    if ingredient in ingredient_mapping:
        return jsonify({"valid": True})
    return jsonify({"valid": False})

@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe_name = recipe_names_mapping.get(recipe_id, "Recipe Not Found")
    video_results = search_youtube(f"how to make {recipe_name}", api_key=YOUTUBE_API_KEY)

    review_data = all_reviews.get(str(recipe_id), {})
    ratings = review_data.get("rating", [])
    reviews = review_data.get("review", [])
    ratings_reviews = list(zip(ratings, reviews))

    # Save viewed recipe
    if "username" in session:
        users = load_users()
        username = session["username"]
        viewed = users[username].setdefault("viewed_recipes", [])
        if recipe_id not in viewed:
            viewed.append(recipe_id)
            save_users(users)

    return render_template("recipe_detail.html",
                           recipe_name=recipe_name,
                           video_results=video_results,
                           ratings_reviews=ratings_reviews)

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    
    users = load_users()
    user_data = users.get(session["username"], {})
    search_history = user_data.get("search_history", [])
    viewed_recipe_ids = user_data.get("viewed_recipes", [])
    
    viewed_recipes = [
        {"id": rid, "name": recipe_names_mapping.get(rid, "Name not found")}
        for rid in viewed_recipe_ids
    ]

    return render_template("profile.html",
                           username=session["username"],
                           search_history=search_history,
                           viewed_recipes=viewed_recipes)



if __name__ == "__main__":
    app.run(debug=True)
