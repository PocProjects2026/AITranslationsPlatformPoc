"""
Demonstrates the foundational concept of text embeddings.
Converts canonical English sentences into dense vector representations.
"""

import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

def load_data(filepath: str) -> List[Dict[str, Any]]:
    """
    Loads sample data containing canonical translation messages.
    
    We load this from a local JSON file to simulate the process of fetching 
    approved records from a translation database or translation memory system.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["messages"]

def initialize_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    """
    Loads the designated embedding model into memory.
    
    In a production environment, systems might utilize larger models outputting 
    512 or 768 dimensions for increased accuracy. We use a smaller, highly efficient 
    model here to ensure the demonstration runs quickly on standard hardware without 
    requiring a dedicated GPU.
    """
    print(f"Initializing embedding model: '{model_name}'...")
    return SentenceTransformer(model_name)

def generate_and_display_embeddings(messages: List[Dict[str, Any]], model: SentenceTransformer) -> None:
    """
    Generates embeddings for each provided message and outputs the mathematical properties 
    of the resulting vectors.
    """
    print("\n--- Generating Embeddings ---")
    
    for msg in messages:
        text = msg["english_text"]
        
        # The encode method passes the string through the neural network and returns a numpy array.
        embedding = model.encode(text)
        
        print(f"\nOriginal Sentence: '{text}'")
        print(f"Vector Data Type:  {type(embedding)}")
        print(f"Vector Shape:      {embedding.shape} (Number of Dimensions)")
        
        # We slice the first 10 dimensions. Printing all 384 dimensions would flood the console 
        # and obscure the learning point.
        first_10_dims = embedding[:10]
        formatted_dims = ", ".join([f"{x:.4f}" for x in first_10_dims])
        print(f"First 10 values:   [{formatted_dims}, ...]")

def main() -> None:
    """
    Main execution pipeline for the embedding demonstration.
    """
    data_path = "sample_data.json"
    messages = load_data(data_path)
    
    model = initialize_model()
    generate_and_display_embeddings(messages, model)
    
    print("\nDemonstration complete.")
    print("Conclusion: Sentences of varying lengths have been successfully converted into uniform fixed-length numerical vectors.")

if __name__ == "__main__":
    main()
