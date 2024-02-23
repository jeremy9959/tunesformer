# %%
import torch
from utils import *
from config import *
from transformers import GPT2Config
from tqdm import tqdm
import json
import faiss

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
filename = "weights/weights.pth"
checkpoint = torch.load("weights/weights.pth")
model.load_state_dict(checkpoint["model"])
model = model.to(device)
model.eval()
# %%
# faiss gpu
res = faiss.StandardGpuResources()
# setup the faiss database
res = faiss.StandardGpuResources()
index = faiss.IndexFlatL2(EMBEDDING_DIM)
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
# load the dataset as a list of dictionaries
# each entry has "control code" and "abc notation" as keys
with open("data/data.json", "r") as f:
    data = json.load(f)

# %%
for item in tqdm(data):
    text = item["control code"] + "\n".join(item["abc notation"].split("\n")[1:])
    input_patch = patchilizer.encode(text, add_special_patches=True)
    input_patch = torch.tensor(input_patch).to(device)
    batch = torch.nn.utils.rnn.pad_sequence(
        [input_patch], batch_first=True, padding_value=0
    ).to(device)
    with torch.no_grad():
        embedding = (
            model.patch_level_decoder(batch)["last_hidden_state"].detach().cpu().numpy()
        )
    gpu_index.add(embedding.mean(1))


faiss.write_index(faiss.index_gpu_to_cpu(gpu_index), "faiss/gpu_index.faiss")

