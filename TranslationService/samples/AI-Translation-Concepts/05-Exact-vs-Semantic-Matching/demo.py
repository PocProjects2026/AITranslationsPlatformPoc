"""
Demonstrates the engineering trade-offs between Exact Matching (Hashing) 
and Semantic Matching (Vector Embeddings).
"""

import json
import hashlib
from typing import Dict, Any, List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

def load_data(filepath: str) -> Dict[str, Any]:
    """Loads the mock database and two different queries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_hash(text: str) -> str:
    """
    Generates a deterministic SHA-256 hash for a given string.
    This acts as a unique digital fingerprint.
    """
    # We encode the string to bytes, hash it, and return the hexadecimal representation.
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def workflow_1_exact_matching(query: str, records: List[str]) -> None:
    """
    Simulates a fast, O(1) hash map lookup, typical of a Redis cache layer.
    """
    print("\n" + "="*60)
    print(" WORKFLOW 1: EXACT MATCHING (O(1) Hash Lookup)")
    print("="*60)
    
    # 1. Database Indexing (Simulated)
    # We pre-compute hashes for all canonical records and store them in a standard dictionary.
    hash_db = {generate_hash(record): record for record in records}
    
    print(f"Query Received: '{query}'")
    
    # 2. Query Hashing
    query_hash = generate_hash(query)
    print(f"Generated SHA-256 Hash:\n{query_hash}")
    
    # 3. Fast Lookup
    if query_hash in hash_db:
        print("\n[SUCCESS] Exact match found in database!")
        print(f"Canonical Document: '{hash_db[query_hash]}'")
        print("\nEngineering Insight:")
        print("Because the hashes match perfectly, we can return this string immediately.")
        print("Embeddings and neural networks are completely unnecessary here.")
        print("This saves significant computational resources and ensures 100% accuracy.")
    else:
        print("\n[FAILED] Hash mismatch. No exact match found.")

def workflow_2_semantic_matching(query: str, records: List[str], model: SentenceTransformer) -> None:
    """
    Simulates a probabilistic vector search when exact matching fails due to phrasing changes.
    """
    print("\n" + "="*60)
    print(" WORKFLOW 2: SEMANTIC MATCHING (Vector Search)")
    print("="*60)
    
    print(f"Query Received: '{query}'")
    
    # 1. Attempt Exact Match First (Standard production fallback pattern)
    query_hash = generate_hash(query)
    hash_db = {generate_hash(record): record for record in records}
    
    print(f"Generated SHA-256 Hash:\n{query_hash}")
    
    if query_hash in hash_db:
        print("Exact match found. (Skipping semantic search).")
        return
        
    print("\n[FAILED] Exact match failed. Hash not found in database.")
    print("Falling back to Semantic Vector Search...\n")
    
    # 2. Fallback to Vector Search
    db_embeddings = model.encode(records)
    query_embedding = model.encode(query)
    
    similarities = cosine_similarity([query_embedding], db_embeddings)[0]
    results = list(zip(records, similarities))
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Format output table
    table_data = [[i+1, msg, f"{score:.4f}"] for i, (msg, score) in enumerate(results)]
    print(tabulate(table_data, headers=["Rank", "Message", "Similarity"], tablefmt="grid"))
    
    print("\nEngineering Insight:")
    print("Because the query phrasing was altered, the SHA-256 hash completely changed.")
    print("Exact matching failed entirely. Semantic search was required to understand that")
    print(f"the query conceptually matched the historical record: '{results[0][0]}'.")

def main() -> None:
    """Main execution pipeline."""
    data = load_data("sample_data.json")
    
    # Run Workflow 1: The query perfectly matches a historical record.
    workflow_1_exact_matching(data["exact_query"], data["canonical_records"])
    
    # Run Workflow 2: The query means the same thing, but uses different words.
    print("\nInitializing embedding model for Workflow 2...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    workflow_2_semantic_matching(data["semantic_query"], data["canonical_records"], model)
    
    print("\nDemonstration complete.")

if __name__ == "__main__":
    main()
