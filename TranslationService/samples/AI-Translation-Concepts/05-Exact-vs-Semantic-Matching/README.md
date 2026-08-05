# 05 - Exact Matching vs Semantic Matching

This module examines a critical system architecture decision: knowing when to use fast, deterministic **Exact Matching** versus slower, probabilistic **Semantic Matching**.

## What this concept is

A robust AI translation system doesn't immediately rely on neural networks for every request. If a user submits a sentence that the system has translated perfectly a million times before, it should use a simple hash lookup (Exact Match) to retrieve it instantly. Semantic Matching (Embeddings) is reserved for when the exact match fails due to phrasing differences.

## Why it exists

Generating embeddings and computing cosine similarity matrices is computationally expensive. It requires CPU/GPU time and memory. Conversely, checking if a string exists in a hash map is an $O(1)$ operation that takes less than a millisecond. Good engineering dictates that you never perform expensive machine learning when a cheap database lookup will suffice.

## Where it is used

This logic sits at the very front of the translation routing pipeline. Every incoming translation request first hits a cache layer (Exact Match). If that results in a "cache miss," the request falls back to the Vector Database (Semantic Match).

## Learning objectives

*   Understand how SHA-256 hashing works for text lookup.
*   Observe why a single changed character breaks an exact match.
*   Implement a fallback mechanism where semantic search saves a failed exact query.

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

The script will demonstrate two workflows. The first workflow proves that identical text can be matched instantly using hashes, completely bypassing the need for AI. The second workflow shows a user phrasing a request differently. The hash lookup fails, and the script gracefully falls back to a semantic vector search to find the correct historical document.
