# %%
import faiss
import torch
import json

# %%
index = faiss.read_index("index.faiss")
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
a = gpu_index.reconstruct_n(0, 210000)

# %%
ncentroids = 1024
niter = 20
verbose = True
d = a.shape[1]
kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=True)
kmeans.train(a)

# %%
D, I = kmeans.index.search(a, 1)
# %%
D, I = index.search(a, 10)
# %%
with open("data.json", "r") as f:
    data = json.load(f)


# %%
for x in I[1000]:
    print(data[x]["abc notation"])
# %%
