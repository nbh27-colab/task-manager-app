import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ✅ Sử dụng PersistentClient theo phiên bản mới
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

collection = client.get_or_create_collection(name="tasks")

embedding_model = SentenceTransformer(EMBEDDING_MODEL)


def embed_and_store_task(task_id: str, description: str):
    embedding = embedding_model.encode(description).tolist()
    collection.add(
        documents=[description],
        ids=[task_id],
        embeddings=[embedding]
    )


def query_similar_tasks(description: str, n_results: int = 3):
    embedding = embedding_model.encode(description).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    return results
