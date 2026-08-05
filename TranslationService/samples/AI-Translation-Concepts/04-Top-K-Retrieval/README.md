# 04 - Top-k Retrieval

This module builds upon Semantic Search by introducing **Top-k Retrieval**, the practice of truncating the ranked list to a fixed number of most relevant results.

## What this concept is

When a system performs a semantic search over a database of millions of records, it generates millions of similarity scores. Top-k retrieval is the mechanism that says, "I don't care about the bottom 999,995 results. Just give me the top 5 (k=5)."

## Why it exists

Large Language Models (LLMs) have a fixed "context window," meaning they can only process a limited amount of text at once. Furthermore, LLM APIs charge by the token. Feeding the entire database into an LLM is both impossible and financially disastrous. By restricting retrieval to a small `k` value, we provide the LLM with only the most concentrated, highly relevant context while keeping costs minimal.

## Where it is used

Every Retrieval-Augmented Generation (RAG) architecture utilizes a Top-k parameter. In an AI translation platform, we might set `k=3` to pull the three most similar historical translations from the Translation Memory to feed into the prompt as examples.

## Learning objectives

*   Understand the function of the `k` parameter in search engineering.
*   Observe how list truncation acts as an information filter.
*   Analyze the trade-offs between retrieving too much context (noise) vs. too little (missing information).

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

The script will run the same underlying semantic search logic as the previous module, but it will demonstrate retrieving different sets of data by modifying the `k` parameter. You will see distinct tables for Top-5, Top-3, and Top-10 results.
