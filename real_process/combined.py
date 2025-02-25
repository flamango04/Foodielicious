import os
from elasticsearch import Elasticsearch
from testing_ingredient import load_ingredient_mapping, convert_ingredients_to_ids, search_recipes_by_ingredient_ids, load_recipe_names
from youtubelinks import search_youtube
from googleapiclient.discovery import build
from dotenv import load_dotenv


def get_recipes_from_ingredients(ingredients):
    # Paths to the CSV files (adjust paths as needed)
    mapping_csv_path = "../dataset/ingr_map.csv"
    recipes_csv_path = "../dataset/RAW_recipes.csv"
    
    # Load ingredient mapping and convert ingredients to their IDs
    ingredient_mapping = load_ingredient_mapping(mapping_csv_path)
    ingredient_ids = convert_ingredients_to_ids(ingredients, ingredient_mapping)

    # Initialize Elasticsearch connection (as done in testing_ingredient.py)
    es = Elasticsearch(
        ["http://localhost:9200"],
        basic_auth=("elastic", "7KYl8Zpm"),
        verify_certs=False 
    )

    # Search for recipes using the ingredient IDs
    index_name = "ingredient"
    match_all = True  # Change to False if you want recipes that match any ingredient
    search_results = search_recipes_by_ingredient_ids(es, index_name, ingredient_ids, match_all)

    # Load recipe names mapping from CSV
    recipe_names_mapping = load_recipe_names(recipes_csv_path)

    # Sort search results by the number of ingredients (optional)
    sorted_results = sorted(
        search_results,
        key=lambda result: len(result["_source"]["ingredient_ids"])
    )

    # Extract and return the recipe names from the results
    recipes = []
    for result in sorted_results:
        recipe_id = result["_source"]["id"]
        recipe_name = recipe_names_mapping.get(recipe_id, "Name not found")
        recipes.append(recipe_name)
    return recipes

def main():
    # Get ingredients from user input (comma-separated)
    ingredients_input = input("Enter ingredients separated by commas: ")
    ingredients = [ingredient.strip() for ingredient in ingredients_input.split(",") if ingredient.strip()]
    
    if not ingredients:
        print("No valid ingredients provided.")
        return

    # Retrieve recipes that match the provided ingredients
    recipes = get_recipes_from_ingredients(ingredients)
    if not recipes:
        print("No recipes found for the given ingredients.")
        return

    print("\nFound recipes:")
    for i, recipe in enumerate(recipes, 1):
        print(f"{i}. {recipe}")

    # Ensure YouTube API key is available in environment variables
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YouTube API key not found. Please set it in your environment or .env file.")
        return

    # For each recipe, search YouTube for how-to video links
    print("\nYouTube video links for the recipes:")
    for recipe in recipes:
        # Construct a search query (e.g., "how to make [recipe]")
        query = f"how to make {recipe}"
        print(f"\nRecipe: {recipe}")
        print(f"Searching YouTube for: {query}")
        video_links = search_youtube(query, api_key)
        if video_links:
            print("Video links:")
            for link in video_links:
                print(link)
        else:
            print("No videos found.")

if __name__ == "__main__":
    main()
