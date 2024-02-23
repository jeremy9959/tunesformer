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


def run_filter(lines):
    score = ""
    for line in lines.replace("\r", "").split("\n"):
        if (
            line[:2]
            in [
                "A:",
                "B:",
                "C:",
                "D:",
                "F:",
                "G",
                "H:",
                "N:",
                "O:",
                "R:",
                "r:",
                "S:",
                "T:",
                "V:",
                "W:",
                "w:",
                "X:",
                "Z:",
            ]
            or line == "\n"
            or line.startswith("%")
        ):
            continue
        else:
            if "%" in line:
                line = line.split("%")
                bar = line[-1]
                line = "".join(line[:-1])
            score += line + "\n"

    return score.strip()


#
EMBEDDING_DIM = 768

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
filename = "weights.pth"
checkpoint = torch.load("weights.pth")
model.load_state_dict(checkpoint["model"])
model = model.to(device)
model.eval()

# setup the faiss database
index = faiss.read_index("index.faiss")

# load the dataset as a list of dictionaries
with open("data.json", "r") as f:
    data = json.load(f)

abcfile = sys.argv[1]
tune_name = abcfile.split("/")[-1].split(".")[0]
with open(abcfile) as f:
    abc = f.read()
# send abc to the stdin of the subprocess add_cc_filter.py and retrieve the output as result
result = subprocess.run(
    ["python", "add_cc_filter.py"], input=abc, text=True, capture_output=True
)
item = eval(result.stdout)

text = item["control code"] + "\n".join(item["abc notation"].split("\n")[1:])
input_patch = patchilizer.encode(text, add_special_patches=True)
input_patch = torch.tensor(input_patch).to(device)
batch = torch.nn.utils.rnn.pad_sequence(
    [input_patch], batch_first=True, padding_value=0
).to(device)
with torch.no_grad():
    embedding = model.patch_level_decoder(batch)["last_hidden_state"].cpu().numpy()

D, I = index.search(embedding.mean(1), 20)
if not os.path.exists(f"results/{tune_name}"):
    os.mkdir(f"results/{tune_name}")
with open(f"results/{tune_name}/reference.abc", "w") as f:
    f.write(abc)
subprocess.run(
    [
        "abc2midi",
        f"results/{tune_name}/reference.abc",
        "-o",
        f"results/{tune_name}/reference.mid",
    ]
)
with open(f"results/{tune_name}/index.txt", "w") as f:
    for x in I[0]:
        f.write(f"{x}\n")

for i, x in enumerate(I[0]):
    with open(f"results/{tune_name}/tune_{str(i).zfill(3)}_{x}.abc", "w") as f:
        f.write(data[x]["abc notation"])
    subprocess.run(
        [
            "abc2midi",
            f"results/{tune_name}/tune_{str(i).zfill(3)}_{x}.abc",
            "-o",
            f"results/{tune_name}/tune_{str(i).zfill(3)}_{x}.mid",
        ]
    )
