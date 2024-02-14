import json
from datasets import load_dataset
import datasets

print(f"Using datasets version {datasets.__version__})

data = load_dataset("sander-wood/irishman")

L = []
for i, x in enumerate(data["train"]):
    L.append(x)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(L, f)
