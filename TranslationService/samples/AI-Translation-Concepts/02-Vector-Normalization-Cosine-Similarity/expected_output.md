# Expected Output: Vector Normalization and Cosine Similarity

When you execute `demo.py`, your console output should look similar to the following:

```text
--- Simplified 3D Vector Example ---
Vector A: [1. 2. 3.]
Vector B: [2. 3. 4.]
Norm (Magnitude) of A: 3.7417
Norm (Magnitude) of B: 5.3852
Normalized A: [0.2673 0.5345 0.8018]
Normalized B: [0.3714 0.5571 0.7428]
Manual Dot Product (Normalized vectors): 0.992583
Sklearn Cosine Similarity function:      0.992583
Are the results mathematically identical?  True


Initializing model for real text test...
--- Real Text Embedding Example ---
Sentence A: 'The network connection timed out during the file transfer.'
Sentence B: 'A timeout occurred while attempting to transfer files over the network.'
Magnitude of Emb A: 1.0000
Magnitude of Emb B: 1.0000
Manual Dot Product (Normalized): 0.865412
Sklearn Cosine Similarity:       0.865412
Are they mathematically identical? True

Demonstration complete.
```

## Why this output is correct

1.  **Magnitude of Emb A and B (1.0000):** You will notice that the `sentence-transformers` model already outputs normalized vectors (magnitude = 1.0). This is a common optimization in production environments because it allows engineers to skip the normalization step entirely when querying databases.
2.  **Identical Similarity Scores:** The manual dot product of the normalized vectors matches the output of `sklearn.metrics.pairwise.cosine_similarity` perfectly. 
3.  **High Similarity Value (0.865):** The two sample sentences are phrased differently but hold the same semantic meaning. A cosine similarity of `0.865` out of `1.0` strongly indicates that they are semantically equivalent.

## How to interpret it

This output proves a core engineering reality: **Cosine Similarity is simply the Dot Product of Normalized Vectors.** 

When building a high-performance vector search engine (like Milvus or Pinecone), engineers do not run expensive cosine calculations at query time. Instead, they store pre-normalized vectors in the database, allowing them to use hardware-optimized dot product operations, massively decreasing latency.
