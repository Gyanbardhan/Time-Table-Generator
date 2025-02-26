import json

def load_data(file_path="input.json"):
    with open(file_path, "r") as f:
        return json.load(f)
