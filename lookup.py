import torch
from utils import *
from config import *
from transformers import GPT2Config
from tqdm import tqdm
import faiss
import sys
import subprocess
import json
import os
import add_cc_filter


#
EMBEDDING_DIM = 768
FAISS_FILE = "faiss/gpu_index.faiss"
DATAFILE = "data/data.json"
OUTPUT_DIR = "{OUTPUT_DIR}"

# load the trained model
device = "cuda" if torch.cuda.is_available() else "cpu"
patchilizer = Patchilizer()
patch_config = GPT2Config(
    num_hidden_layers=PATCH_NUM_LAYERS,
    max_length=PATCH_LENGTH,
    max_position_embeddings=PATCH_LENGTH,
    vocab_size=1,
)
char_config = GPT2Config(
    num_hidden_layers=CHAR_NUM_LAYERS,
    max_length=PATCH_SIZE,
    max_position_embeddings=PATCH_SIZE,
    vocab_size=128,
)
model = TunesFormer(patch_config, char_config, share_weights=SHARE_WEIGHTS)
filename = "weights/weights.pth"
checkpoint = torch.load(filename)
model.load_state_dict(checkpoint["model"])
model = model.to(device)
model.eval()

# setup the faiss database
index = faiss.read_index(FAISS_FILE)

# load the dataset as a list of dictionaries
with open(DATAFILE, "r") as f:
    data = json.load(f)


abcfile = sys.argv[1]
tune_name = abcfile.split("/")[-1].split(".")[0]
with open(abcfile) as f:
    abc = f.read()

# add the control codes following tunesformer code
item = add_cc_filter.add_control_codes(abc)

text = item["control code"] + "\n".join(item["abc notation"].split("\n")[1:])
input_patch = patchilizer.encode(text, add_special_patches=True)
input_patch = torch.tensor(input_patch).to(device)
batch = torch.nn.utils.rnn.pad_sequence(
    [input_patch], batch_first=True, padding_value=0
).to(device)
with torch.no_grad():
    embedding = model.patch_level_decoder(batch)["last_hidden_state"].cpu().numpy()

D, I = index.search(embedding.mean(1), 20)

if not os.path.exists(f"{OUTPUT_DIR}/{tune_name}"):
    os.mkdir(f"{OUTPUT_DIR}/{tune_name}")
with open(f"{OUTPUT_DIR}/{tune_name}/reference.abc", "w") as f:
    f.write(abc)
subprocess.run(
    [
        "abc2midi",
        f"{OUTPUT_DIR}/{tune_name}/reference.abc",
        "-o",
        f"{OUTPUT_DIR}/{tune_name}/reference.mid",
    ]
)
with open(f"{OUTPUT_DIR}/{tune_name}/index.txt", "w") as f:
    for x in I[0]:
        f.write(f"{x}\n")

for i, x in enumerate(I[0]):
    with open(f"{OUTPUT_DIR}/{tune_name}/tune_{str(i).zfill(3)}_{x}.abc", "w") as f:
        f.write(data[x]["abc notation"])
    subprocess.run(
        [
            "abc2midi",
            f"{OUTPUT_DIR}/{tune_name}/tune_{str(i).zfill(3)}_{x}.abc",
            "-o",
            f"{OUTPUT_DIR}/{tune_name}/tune_{str(i).zfill(3)}_{x}.mid",
        ]
    )
