"""
Demonstrates how to perform a semantic search.
Embeds a query, compares it against a database of embedded messages, 
and ranks the results by cosine similarity.
"""

import json
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

def load_data(filepath: str) -> Dict[str, Any]:
    """
    Loads the search query and the mock database of historical messages.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def rank_results(query_embedding: np.ndarray, db_embeddings: np.ndarray, messages: List[str]) -> List[Tuple[str, float]]:
    """
    Computes cosine similarity between the query and all database entries,
    then sorts them from highest to lowest similarity to establish rank.
    """
    # cosine_similarity expects 2D arrays and returns a 2D matrix.
    # Since we only have one query, we extract the first row [0].
    # Example output: array([0.12, 0.88, 0.05, ...])
    similarities = cosine_similarity([query_embedding], db_embeddings)[0]
    
    # Pair each original text message with its computed similarity score
    results = list(zip(messages, similarities))
    
    # Sort the results in descending order based on the similarity score (index 1 of the tuple)
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def display_ranked_table(ranked_results: List[Tuple[str, float]]) -> None:
    """
    Formats the ranked results into a readable console table using the tabulate library.
    """
    table_data = []
    
    for rank, (msg, score) in enumerate(ranked_results, start=1):
        # We want to highlight the top-ranked result visually to simulate
        # what a system might select as the primary context.
        if rank == 1:
            rank_display = f"--> {rank} <--"
            msg_display = f"** {msg} **"
        else:
            rank_display = str(rank)
            msg_display = msg
            
        # Format the score to 4 decimal places for clean reading
        table_data.append([rank_display, msg_display, f"{score:.4f}"])
        
    headers = ["Rank", "Message", "Similarity Score"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main() -> None:
    """
    Main execution pipeline for the Semantic Search demonstration.
    """
    data = load_data("sample_data.json")
    query_text = data["query"]
    messages = data["messages"]
    
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Step 1: Embed the "Database"
    # In a production environment, this step is done asynchronously.
    # Vectors are generated once and stored in a specialized Vector DB (e.g., Pinecone).
    print(f"\nEmbedding {len(messages)} database messages...")
    db_embeddings = model.encode(messages)
    
    # Step 2: Embed the User Query
    # This happens at runtime when the user hits 'Search'.
    print(f"Embedding query: '{query_text}'...")
    query_embedding = model.encode(query_text)
    
    # Step 3: Compute Similarity and Rank
    print("\nComputing cosine similarity and ranking results...\n")
    ranked_results = rank_results(query_embedding, db_embeddings, messages)
    
    # Step 4: Display Output
    display_ranked_table(ranked_results)

if __name__ == "__main__":
    main()
