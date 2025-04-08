#%%
import csv
import json

# Input and output file paths
csv_file = "PP_recipes.csv"  # Replace with your CSV file name
json_file = "PP_recipes.json"  # Output JSON file name

# Convert CSV to Elasticsearch Bulk JSON format
with open(csv_file, "r") as csv_f, open(json_file, "w") as json_f:
    reader = csv.DictReader(csv_f)  # Read CSV file with headers
    for idx, row in enumerate(reader):
        # Create an index action for Elasticsearch bulk upload
        action = {"index": {"_index": "my_index", "_id": idx + 1}}
        json_f.write(json.dumps(action) + "\n")
        
        # Process each row into a JSON document
        # Convert fields to their appropriate types
        row["id"] = int(row["id"])
        row["i"] = int(row["i"])
        row["name_tokens"] = json.loads(row["name_tokens"])
        row["ingredient_tokens"] = json.loads(row["ingredient_tokens"])
        row["steps_tokens"] = json.loads(row["steps_tokens"])
        row["techniques"] = json.loads(row["techniques"])
        row["calorie_level"] = int(row["calorie_level"])
        row["ingredient_ids"] = json.loads(row["ingredient_ids"])

        # Write the JSON document
        json_f.write(json.dumps(row) + "\n")

print(f"JSON data written to {json_file}")


#%%
import csv
import json
import ast

input_csv_file = "dataset/RAW_recipes_name_ingredient.csv"
output_json_file = "dataset/RAW_recipes_name_ingredient.json"

recipes = []

with open(input_csv_file, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        try:
            ingredients = ast.literal_eval(row["ingredients"])
            recipe = {
                "name": row["name"],
                "ingredients": ingredients
            }
            recipes.append(recipe)
        except (ValueError, SyntaxError):
            pass

with open(output_json_file, mode="w", encoding="utf-8") as outfile:
    json.dump(recipes, outfile, indent=4)


#%%
import csv
import json
import ast
from tqdm import tqdm

input_csv_file = "dataset/RAW_recipes_name_ingredient.csv"
output_bulk_file = "dataset/RAW_recipes_name_ingredient_bulk.json"
index_name = "recipes"

import json

# Input and output file paths
input_json_file = "path/to/your/input.json"  # Replace with the path to your input JSON file
output_bulk_file = "path/to/your/output.json"  # Replace with the path to your output Elasticsearch bulk file
index_name = "recipes"  # Elasticsearch index name

# Read the JSON file and process it
with open(input_json_file, mode="r", encoding="utf-8") as infile, open(output_bulk_file, mode="w", encoding="utf-8") as outfile:
    try:
        # Load the entire JSON data
        data = json.load(infile)
        
        # Process each record in the JSON data
        for doc_id, item in enumerate(data, start=1):  # Start unique `_id` from 1
            try:
                # Write action line for Elasticsearch Bulk API
                action_line = {"index": {"_index": index_name, "_id": doc_id}}
                outfile.write(json.dumps(action_line, ensure_ascii=False) + "\n")
                
                # Transform the document: Use "id" as "name"
                document = {
                    "name": item["id"],  # Rename "id" to "name"
                    "ingredient_ids": item["ingredient_ids"]  # Keep the "ingredient_ids"
                }
                outfile.write(json.dumps(document, ensure_ascii=False) + "\n")
            
            except KeyError as e:
                # Handle cases where expected keys are missing
                print(f"KeyError processing document with _id {doc_id}: {e}")
            except (ValueError, SyntaxError) as e:
                # Handle issues with JSON structure
                print(f"Error processing document with _id {doc_id}: {e}")
        
        # Ensure the final file ends with a newline
        outfile.write("\n")
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_json_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file '{input_json_file}': {e}")

print(f"Bulk JSON file successfully generated at: {output_bulk_file}")

