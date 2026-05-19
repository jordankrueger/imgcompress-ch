import json
from rembg import new_session

with open("backend/image_converter/config/rembg.json", "r", encoding="utf-8") as f:
    model_name = json.load(f).get("model_name", "u2net")

new_session(model_name)
print(f"rembg model cached: {model_name}")
