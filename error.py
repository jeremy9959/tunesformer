## Verifying that load_dataset works -- it does, under python 3.11, but fails at 3.12

from datasets import load_dataset

data = load_dataset("sander-wood/irishman")
print(data)
