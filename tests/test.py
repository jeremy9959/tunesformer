import faiss
import numpy as np


# Run this to verify that the GPU works
 
res = faiss.StandardGpuResources()
index = faiss.IndexFlatL2(20)
gpu_index = faiss.index_cpu_to_gpu(res,0,index)
x = np.random.normal(0,1,size=(200,20))
gpu_index.add(x)
 
y = np.random.normal(0,1,size=(5,20))
D, I = gpu_index.search(y,1)


kmeans = faiss.Kmeans(20,2,niter=5,verbose=True,gpu=True) 
kmeans.train(x)

