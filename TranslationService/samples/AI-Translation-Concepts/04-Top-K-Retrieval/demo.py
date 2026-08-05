"""
Demonstrates Top-k Retrieval.
Builds on semantic search by truncating the ranked results to a specific 'k' value,
which is essential for managing context windows in Large Language Models.
"""

import json
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

def load_data(filepath: str) -> Dict[str, Any]:
    """Loads the mock database and query."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def retrieve_top_k(query_embedding: np.ndarray, db_embeddings: np.ndarray, messages: List[str], k: int) -> List[Tuple[str, float]]:
    """
    Computes similarities, sorts them, and returns ONLY the top 'k' results.
    This simulates how a vector database (like Pinecone or Qdrant) processes a query.
    """
    # 1. Compute cosine similarity for all entries
    similarities = cosine_similarity([query_embedding], db_embeddings)[0]
    
    # 2. Pair text with scores
    results = list(zip(messages, similarities))
    
    # 3. Sort descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    # 4. Truncate the list. This is the core mechanic of Top-k.
    # We take a slice of the list from index 0 up to 'k'. 
    # Everything else is discarded.
    return results[:k]

def display_results(results: List[Tuple[str, float]], k: int) -> None:
    """Formats and prints the retrieved subset."""
    print(f"\n--- Top-{k} Retrieved Results ---")
    
    table_data = []
    for i, (msg, score) in enumerate(results):
        # We use i+1 to show the actual rank (1-indexed)
        table_data.append([i+1, msg, f"{score:.4f}"])
        
    print(tabulate(table_data, headers=["Rank", "Message", "Similarity"], tablefmt="grid"))

def main() -> None:
    """Main execution pipeline."""
    data = load_data("sample_data.json")
    query_text = data["query"]
    messages = data["messages"]
    
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Embedding {len(messages)} database entries and 1 query...")
    db_embeddings = model.encode(messages)
    query_embedding = model.encode(query_text)
    
    print(f"\nTarget Query: '{query_text}'")
    
    # --- Experiment 1: Top-5 ---
    # A balanced approach, providing decent context without excessive token usage.
    top_5_results = retrieve_top_k(query_embedding, db_embeddings, messages, k=5)
    display_results(top_5_results, k=5)
    
    # --- Experiment 2: Top-3 ---
    # Used when strict latency requirements or tight budget constraints exist.
    top_3_results = retrieve_top_k(query_embedding, db_embeddings, messages, k=3)
    display_results(top_3_results, k=3)
    
    # --- Experiment 3: Top-10 ---
    # Provides heavy context. Notice how the similarity scores begin to drop significantly
    # at the bottom of the Top-10, indicating we are retrieving irrelevant "noise".
    top_10_results = retrieve_top_k(query_embedding, db_embeddings, messages, k=10)
    display_results(top_10_results, k=10)
    
    print("\nDemonstration complete.")
    print("Notice that lower-ranked, irrelevant results are successfully filtered out of the smaller 'k' subsets.")

if __name__ == "__main__":
    main()
