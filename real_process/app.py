import os
import time
import json
import requests
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from testing_ingredient import load_recipe_details, load_ingredient_mapping, convert_ingredients_to_ids, search_recipes_by_ingredient_ids, load_recipe_names
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
    return redirect(url_for("register_email_step1"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = {}
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        users = load_users()

        user = users.get(email)

        if not user:
            error["email"] = "Email not found. Want to register?"
        elif user["password"] != password:
            error["password"] = "Incorrect password."

        if not error:
            session["username"] = user["username"] 
            session["email"] = email             
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
        basic_auth=("elastic", "dbsFOxSUAvzyH_K5s6zH"),
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
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_ingredients = request.form.get("selected_ingredients", "").strip()
        session["selected_ingredients"] = selected_ingredients
        ingredients = [i.strip() for i in selected_ingredients.split(",") if i.strip()]
        recipe_data = get_recipe_data_from_ingredients(ingredients)
        if "email" in session:
            users = load_users()
            email = session["email"]
            if "search_history" not in users[email]:
                users[email]["search_history"] = []
            users[email]["search_history"].append(selected_ingredients)
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


from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import random
import re


serializer = URLSafeTimedSerializer(app.secret_key)

app.config.update({
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USERNAME": "zihe030716@gmail.com",  
    "MAIL_PASSWORD": "bbvgjaqcvkjpbjfu",    
    "MAIL_DEFAULT_SENDER": "zihe030716@gmail.com"
})

mail = Mail(app)


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_verification_code(email, code):
    msg = Message(
        subject="Your RecipeApp Verification Code",
        recipients=[email],
        body=f"Your verification code is: {code}"
    )
    mail.send(msg)
    return True

@app.route("/register_email", methods=["GET", "POST"])
def register_email_step1():
    error = None
    if request.method == "POST":
        users = load_users()
        email = request.form.get("email", "").strip().lower()
        if not is_valid_email(email):
            error = "Please enter a valid email address."
        elif email in users:
            error = "This email is already registered."
        else:
            code = str(random.randint(100000, 999999))
            session["verify_code"] = code
            session["verify_email"] = email
            send_verification_code(email, code)
            return redirect(url_for("register_email_step2"))
    return render_template("register_step1.html", error=error)

@app.route("/register_verify", methods=["GET", "POST"])
def register_email_step2():
    error = None
    if request.method == "POST":
        input_code = request.form.get("code", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()
        email = session.get("verify_email")

        if input_code != session.get("verify_code"):
            error = "Incorrect verification code."
        else:
            users[email] = {
                "username": username,
                "password": password,
                "search_history": [],
                "viewed_recipes": []
            }
            save_users(users)
            session["username"] = username 
            session["email"] = email      
            session.pop("verify_code", None)
            session.pop("verify_email", None)
            return redirect(url_for("index"))

    return render_template("register_step2.html", error=error)


@app.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        users = load_users()

        if not is_valid_email(email):
            error = "Please enter a valid email address."
        elif email not in users:
            error = "No account is linked with this email."
        else:
            code = str(random.randint(100000, 999999))
            session["reset_code"] = code
            session["reset_email"] = email
            send_verification_code(email, code)
            return redirect(url_for("reset_verify"))

    return render_template("reset_request.html", error=error)


@app.route("/reset_verify", methods=["GET", "POST"])
def reset_verify():
    error = None
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        new_password = request.form.get("password", "").strip()
        email = session.get("reset_email")
        users = load_users()

        if code != session.get("reset_code"):
            error = "Incorrect verification code."
        elif email not in users:
            error = "User not found."
        else:
            users[email]["password"] = new_password
            save_users(users)
            session.pop("reset_code", None)
            session.pop("reset_email", None)
            return redirect(url_for("login"))

    return render_template("reset_verify.html", error=error)

@app.route('/ask', methods=['POST'])
def ask_gpt():
    try:
        user_input = request.json.get("question", "").strip()
        if not user_input:
            return jsonify({"answer": "Please enter a valid question."}), 400

        # Format prompt for a cooking assistant
        prompt = f"Answer the following cooking-related question:\n{user_input}"

        headers = {
            "Authorization": f"Bearer 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"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "return_full_text": True
            }
        }

        # Replace model URL if using a different one
        hf_response = requests.post(
            "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
            headers=headers,
            json=payload
        )

        if hf_response.status_code != 200:
            error_info = hf_response.json()
            return jsonify({"answer": f"Error: {error_info.get('error', 'Unknown error')}"}), 500

        result = hf_response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return jsonify({"answer": result[0]["generated_text"]})
        else:
            return jsonify({"answer": "Sorry, I couldn't understand the response."})

    except Exception as e:
        return jsonify({"answer": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)