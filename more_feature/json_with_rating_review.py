#%%
import pandas as pd
import json

df = pd.read_csv('../dataset/RAW_interactions.csv')

grouped = df.groupby('recipe_id').agg({
    'rating': lambda x: x.tolist(),
    'review': lambda x: x.tolist()
}).reset_index()

result = {}
for _, row in grouped.iterrows():
    recipe_id = row['recipe_id']
    ratings = row['rating']
    reviews = row['review']
    result[str(recipe_id)] = {
        'rating': ratings,
        'review': reviews
    }

with open('recipes_reviews.json', 'w') as f:
    json.dump(result, f, indent=2)

print("JSON file 'recipes_reviews.json' created successfully.")

#%%
import pandas as pd
import json

# Load IDs from recipes_reviews.json
with open('recipes_reviews.json', 'r') as f:
    recipes_reviews = json.load(f)

reviews_json_ids = set(int(recipe_id) for recipe_id in recipes_reviews.keys())

# Load IDs from elastic_bulk_recipes.json
elastic_ids = set()
with open('../dataset/elastic_bulk_recipes.json', 'r') as f:
    for line in f:
        data = json.loads(line)
        if 'id' in data:
            elastic_ids.add(data['id'])


# Load CSV and extract IDs
raw_df = pd.read_csv('../dataset/RAW_recipes.csv')
csv_ids = set(raw_df['id'].unique())

# Check IDs from recipes_reviews.json against elastic_bulk_recipes.json
missing_in_elastic = elastic_ids - reviews_json_ids

if missing_in_elastic:
    print(f"The following IDs from recipes_reviews.json are missing in elastic_bulk_recipes.json: {missing_in_elastic}")
else:
    print("All IDs from recipes_reviews.json are present in elastic_bulk_recipes.json.")

# Check IDs from recipes_reviews.json against RAW_recipes.csv
missing_in_csv = reviews_json_ids - csv_ids

if missing_in_csv:
    print(f"The following IDs from recipes_reviews.json are missing in RAW_recipes.csv: {missing_in_csv}")
else:
    print("All IDs from recipes_reviews.json are present in RAW_recipes.csv.")