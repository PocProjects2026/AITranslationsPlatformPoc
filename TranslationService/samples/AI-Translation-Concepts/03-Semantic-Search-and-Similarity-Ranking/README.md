# 03 - Semantic Search and Similarity Ranking

This module demonstrates a complete **Semantic Search** workflow, where a user's query is compared against a database of pre-existing documents to find the most relevant matches based on meaning, rather than exact keyword overlap.

## What this concept is

Semantic search leverages embeddings to evaluate the contextual relationship between texts. By embedding a database of historical records and then embedding an incoming query, an AI system can compute the similarity scores for all records and rank them from most to least relevant.

## Why it exists

Users rarely type the exact same phrasing used in technical documentation or historical translations. If a user searches for "can't log in," but the database only contains "authentication failure," keyword search fails entirely. Semantic search understands that these phrases occupy the same conceptual space and successfully bridges the gap between the user's intent and the system's terminology.

## Where it is used

This is the core retrieval mechanism for Translation Memory systems, customer support chatbots, and standard RAG (Retrieval-Augmented Generation) pipelines. It ensures that the LLM is fed the most contextually relevant historical examples before generating a final answer or translation.

## Learning objectives

*   Understand how to scale vector comparisons from a 1-to-1 operation to a 1-to-N operation.
*   Observe how similarity scores correlate with human-perceived semantic relevance.
*   Format and rank the output matrix into actionable results.

## Required libraries

*   `sentence-transformers`
*   `numpy`
*   `scikit-learn`
*   `tabulate`

## Installation

```bash
pip install -r requirements.txt
```

## How to run

```bash
python demo.py
```

## Expected result

The script will embed a set of eight canonical messages and a single user query. It will calculate the cosine similarity matrix, sort the results descending by similarity score, and print a formatted table showing exactly which messages are closest in meaning to the query.
