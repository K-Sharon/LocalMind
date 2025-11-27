import faiss
import numpy as np

def create_vector_store(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search(query_embedding, index, k=5):
    distances, indices = index.search(query_embedding, k)
    return indices
