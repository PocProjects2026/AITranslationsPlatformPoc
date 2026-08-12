"""
Demonstrates the final step in a RAG (Retrieval-Augmented Generation) pipeline: Prompt Construction.
Embeds the query, retrieves the Top-k historical translations, 
and injects them into a strict system prompt designed for an LLM.
"""

import json
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def load_data(filepath: str) -> Dict[str, Any]:
    """Loads the mock query and translation memory database."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def retrieve_top_k(query_embedding: np.ndarray, db_embeddings: np.ndarray, records: List[Dict[str, str]], k: int) -> List[Dict[str, str]]:
    """
    Executes the semantic search and returns the dictionary records of the top 'k' matches.
    """
    similarities = cosine_similarity([query_embedding], db_embeddings)[0]
    results = list(zip(records, similarities))
    results.sort(key=lambda x: x[1], reverse=True)
    
    # We strip out the similarity score here, returning only the data payloads
    # because the LLM does not need to see the raw cosine math.
    return [record for record, score in results[:k]]

def construct_prompt(query: str, target_lang: str, context_records: List[Dict[str, str]]) -> str:
    """
    Constructs the final text string that will be transmitted to the Large Language Model.
    Notice the strict use of formatting and delimiters to prevent LLM confusion.
    """
    # 1. Define the System Instructions (The "Persona")
    system_prompt = (
        f"You are a professional software localization expert.\n"
        f"Translate the user's message into {target_lang}.\n"
        f"Use the provided historical translations as context to maintain consistent terminology.\n"
        f"Do not copy the examples directly unless they are an exact match. "
        f"You must generate a new, accurate translation based on the provided context."
    )
    
    # 2. Format the Context block (The "Retrieved Examples")
    context_block = "--- HISTORICAL CONTEXT ---\n"
    for i, record in enumerate(context_records, 1):
        context_block += f"Example {i}:\n"
        context_block += f"English:     {record['english']}\n"
        context_block += f"Translation: {record['french']}\n\n"
        
    # 3. Format the User Message (The "Task")
    user_message = f"--- USER MESSAGE ---\n{query}\n"
    
    # 4. Assemble the final string
    final_prompt = f"{system_prompt}\n\n{context_block}{user_message}\nTRANSLATION:"
    
    return final_prompt

def main() -> None:
    """Main execution pipeline."""
    data = load_data("sample_data.json")
    query = data["query"]
    target_lang = data["language_target"]
    historical_records = data["historical_translations"]
    
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Step 1: We only embed the English side of the historical records for the search.
    english_texts = [record["english"] for record in historical_records]
    db_embeddings = model.encode(english_texts)
    query_embedding = model.encode(query)
    
    # Step 2: Retrieve the context
    print("\nRetrieving Top-3 relevant historical translations via Semantic Search...")
    top_3_records = retrieve_top_k(query_embedding, db_embeddings, historical_records, k=3)
    
    # Step 3: Construct the payload
    print("\nConstructing LLM Prompt...\n")
    print("="*60)
    print(" FINAL PROMPT DELIVERED TO LLM API")
    print("="*60)
    
    final_prompt = construct_prompt(query, target_lang, top_3_records)
    print(final_prompt)
    print("="*60)
    
    # Step 4: Output Engineering Insights
    print("\nEngineering Insight:")
    print("The LLM now possesses both instructions and specialized vocabulary (e.g., 'faible', 'chargeur').")
    print("The retrieved examples are CONTEXT ONLY. They guide the model's stylistic choices,")
    print("ensuring it generates a translation consistent with previous enterprise data,")
    print("rather than hallucinating a generic dictionary translation.")

if __name__ == "__main__":
    main()
