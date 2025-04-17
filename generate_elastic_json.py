#%%
import csv
import json

input_csv_file = r"C:\Users\megad\CSE_5914_Capstone_Foodielicious\Foodielicious\dataset\PP_recipes.csv"  
output_bulk_file = r"C:\Users\megad\CSE_5914_Capstone_Foodielicious\Foodielicious\dataset\elastic_bulk_recipes.json"  
index_name = "ingredient" 

try:
    with open(input_csv_file, mode="r", encoding="utf-8") as csvfile, open(output_bulk_file, mode="w", encoding="utf-8") as outfile:
        reader = csv.DictReader(csvfile)
        
        for doc_id, row in enumerate(reader, start=1): 
            try:
                action_line = {"index": {"_index": index_name, "_id": doc_id}}
                outfile.write(json.dumps(action_line, ensure_ascii=False) + "\n")
                
                document = {
                    "id": int(row["id"]), 
                    "ingredient_ids": json.loads(row["ingredient_ids"]), 
                }
                outfile.write(json.dumps(document, ensure_ascii=False) + "\n")
            
            except KeyError as e:
                print(f"KeyError processing document with _id {doc_id}: Missing column {e}")
            except (ValueError, SyntaxError) as e:
                print(f"Error processing document with _id {doc_id}: {e}")
    
    print(f"Bulk JSON successfully generated: {output_bulk_file}")

except FileNotFoundError:
    print(f"error: '{input_csv_file}'。")
except Exception as e:
    print(f"error: {e}")
