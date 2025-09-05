# database/vectordb.py

import chromadb
from chromadb.utils import embedding_functions
import os
from typing import Optional

# Define the path for the ChromaDB data
# It will be created in a 'chroma_data' subdirectory in your project root
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_data")

# Initialize ChromaDB client
# This will persist the data to the specified path
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Define an embedding function
# The 'SentenceTransformerEmbeddingFunction' with 'all-MiniLM-L6-v2' is a functional
# and widely used embedding model. It's not a dummy.
# For further "upgrade" in embedding quality, consider:
# 1. Using a larger Sentence Transformer model (e.g., "all-mpnet-base-v2").
# 2. Integrating with external embedding services (e.g., OpenAI, Google Vertex AI)
#    which might require API keys and different setup.
try:
    default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
except ImportError:
    print("Warning: 'sentence-transformers' not installed. Please run 'pip install sentence-transformers' if you want to use the default embedding function.")
    print("Falling back to a dummy embedding function. AI features relying on embeddings will not work.")
    # Fallback to a dummy function if sentence-transformers is not available
    def dummy_embed_function(texts: list[str]) -> list[list[float]]:
        print("Using dummy embedding function. Embeddings will be random.")
        return [[0.0] * 384 for _ in texts] # all-MiniLM-L6-v2 produces 384-dim embeddings
    default_ef = dummy_embed_function


# Get or create a collection for tasks
# A collection is where your embeddings and associated metadata are stored
TASK_COLLECTION_NAME = "tasks_collection"
task_collection = client.get_or_create_collection(
    name=TASK_COLLECTION_NAME,
    embedding_function=default_ef # Pass the embedding function here
)

def add_task_embedding(task_id: int, task_text: str, owner_id: int, metadata: Optional[dict] = None):
    """
    Adds an embedding for a task to the ChromaDB collection.
    task_text is the content to be embedded (e.g., task title + description).
    owner_id is included directly for convenience and also added to metadata.
    metadata: Optional dictionary for filtering and additional information.
    """
    if metadata is None:
        metadata = {}
    metadata.update({"owner_id": owner_id}) # Ensure owner_id is in metadata for filtering

    if not task_text:
        print(f"Warning: No text provided for task {task_id}. Skipping embedding.")
        return
    
    task_collection.add(
        documents=[task_text],
        metadatas=[metadata],
        ids=[str(task_id)] # IDs must be strings
    )
    print(f"Added embedding for task {task_id} to ChromaDB.")

def query_similar_tasks(query_text: str, n_results: int = 5, owner_id: Optional[int] = None):
    """
    Queries ChromaDB for tasks similar to the query_text.
    Optionally filters by owner_id.
    Returns a list of dictionaries with 'id', 'distance', 'document', 'metadata'.
    """
    where_clause = {"owner_id": owner_id} if owner_id else {}

    results = task_collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where_clause
    )
    
    # Format results for easier use
    formatted_results = []
    if results and results.get('ids') and results['ids'][0]:
        for i in range(len(results['ids'][0])):# Ensure results['ids'][0] is not empty
            formatted_results.append({
                "id": int(results['ids'][0][i]),
                "distance": results['distances'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            })
    return formatted_results

def delete_task_embedding(task_id: int):
    """
    Deletes a task embedding from ChromaDB.
    """
    try:
        task_collection.delete(ids=[str(task_id)])
        print(f"Deleted embedding for task {task_id} from ChromaDB.")
    except Exception as e:
        print(f"Error deleting embedding for task {task_id}: {e}")

def update_task_embedding(task_id: int, new_task_text: str, owner_id: int, new_metadata: Optional[dict] = None):
    """
    Updates a task's embedding in ChromaDB.
    """
    if new_metadata is None:
        new_metadata = {}
    new_metadata.update({"owner_id": owner_id})

    if not new_task_text:
        print(f"Warning: No new text provided for task {task_id}. Skipping embedding update.")
        return
    
    task_collection.update(
        ids=[str(task_id)],
        documents=[new_task_text],
        metadatas=[new_metadata]
    )
    print(f"Updated embedding for task {task_id} in ChromaDB.")

