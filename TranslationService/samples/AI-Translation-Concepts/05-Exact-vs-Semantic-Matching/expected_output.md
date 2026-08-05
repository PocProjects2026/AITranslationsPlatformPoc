# Expected Output: Exact vs Semantic Matching

When you run `demo.py`, you will see two clear workflows demonstrating how a production system routes queries based on exactness.

```text
============================================================
 WORKFLOW 1: EXACT MATCHING (O(1) Hash Lookup)
============================================================
Query Received: 'The package has shipped.'
Generated SHA-256 Hash:
b18a38a719c8f37d363d5... (truncated for readability)

[SUCCESS] Exact match found in database!
Canonical Document: 'The package has shipped.'

Engineering Insight:
Because the hashes match perfectly, we can return this string immediately.
Embeddings and neural networks are completely unnecessary here.
This saves significant computational resources and ensures 100% accuracy.


Initializing embedding model for Workflow 2...

============================================================
 WORKFLOW 2: SEMANTIC MATCHING (Vector Search)
============================================================
Query Received: 'My order has already been sent.'
Generated SHA-256 Hash:
f4e27b9c0d51a62e78... (truncated for readability)

[FAILED] Exact match failed. Hash not found in database.
Falling back to Semantic Vector Search...

+--------+----------------------------------------+--------------+
|   Rank | Message                                |   Similarity |
+========+========================================+==============+
|      1 | The package has shipped.               |       0.5842 |
+--------+----------------------------------------+--------------+
|      2 | Your invoice is attached.              |       0.1234 |
+--------+----------------------------------------+--------------+
|      3 | Please update your password.           |       0.0412 |
+--------+----------------------------------------+--------------+
|      4 | Your account is temporarily suspended. |      -0.0341 |
+--------+----------------------------------------+--------------+

Engineering Insight:
Because the query phrasing was altered, the SHA-256 hash completely changed.
Exact matching failed entirely. Semantic search was required to understand that
the query conceptually matched the historical record: 'The package has shipped.'.
```

## Why this output is correct

1.  **Workflow 1:** The query exactly matched the stored database string character for character. Therefore, their SHA-256 hashes matched identically. The system successfully executed an immediate dictionary lookup.
2.  **Workflow 2:** The user submitted a sentence with a very similar meaning, but entirely different words. Because the string changed, the resulting SHA-256 hash was completely different. The hash lookup failed. The system automatically initialized the embedding model, converted the string to a vector, and successfully identified "The package has shipped." as the closest conceptual match.

## How to interpret it

This demonstrates the core architectural pattern of **caching**. Exact matching acts as a high-speed cache. Semantic matching acts as the intelligent, but slower, fallback mechanism. Together, they create a system that is both efficient and robust against human variation.
