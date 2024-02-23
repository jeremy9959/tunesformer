# %%
import faiss
import torch
import json

# %%
index = faiss.read_index("faiss.index")
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
a = gpu_index.reconstruct_n(0, 210000)

# %%
ncentroids = 1024
niter = 200
verbose = True
d = a.shape[1]
kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=True)
kmeans.train(a)

D, I = gpu_index.search(kmeans.centroids,1)

with open("data.json", "r") as f:
    data = json.load(f)


# %%
for x in I:
    print(data[x[0]]["abc notation"])
# %%
