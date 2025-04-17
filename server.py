import csv
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification

app = FastAPI()

model = AutoModelForZeroShotImageClassification.from_pretrained("openai/clip-vit-base-patch32")
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

CSV_FILE_PATH = "dataset/ingr_map.csv"

def load_ingredients(csv_file_path):
    ingredients = []
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ingredients.append({
                "raw_ingr": row["raw_ingr"],
                "processed": row["processed"],
                "id": row["id"]
            })
    return ingredients

INGREDIENTS_DB = load_ingredients(CSV_FILE_PATH)


class IngredientRequest(BaseModel):
    keyword: str


def encode_text(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = model.text_model(**inputs).pooler_output
    return text_features

 
def find_similar_ingredients(keyword):
    keyword_embedding = encode_text(keyword)
    similarities = []

    for item in INGREDIENTS_DB:
        processed_embedding = encode_text(item["processed"])
        similarity = torch.cosine_similarity(keyword_embedding, processed_embedding).item()
        similarities.append((item, similarity))

    
    sorted_results = sorted(similarities, key=lambda x: x[1], reverse=True)[:9]
    return [{"raw_ingr": item["raw_ingr"], "processed": item["processed"], "id": item["id"], "similarity": similarity}
            for item, similarity in sorted_results]
@app.post("/search/")
def search_ingredients(request: IngredientRequest):
    results = find_similar_ingredients(request.keyword)
    return {"results": results}

# 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)