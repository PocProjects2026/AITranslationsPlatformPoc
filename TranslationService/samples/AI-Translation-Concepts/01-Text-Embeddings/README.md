# 01 - Text Embeddings

This module introduces the foundational concept behind modern search and AI translation: **Text Embeddings**.

## What this concept is

Text embeddings are dense mathematical representations of text. When an embedding model processes a sentence, it converts that sentence into an array of floating-point numbers. This array captures the semantic meaning of the text.

## Why it exists

Computers cannot inherently understand human language. They understand numbers. Embeddings bridge this gap by encoding the relationship between words and concepts into a format that a machine can process algebraically.

## Where it is used

In our AI translation platform, every approved canonical translation is converted into an embedding and stored in a vector database. When a user requests a new translation, we embed their request and compare it against the stored vectors to find similar previous translations.

## Learning objectives

*   Understand how a string of text translates into a numerical vector.
*   Observe the fixed dimensionality of an embedding model.
*   Recognize that different sentences yield vectors of the exact same length.

## Required libraries

*   `sentence-transformers`: For loading the pre-trained embedding model.

## Installation

```bash
pip install -r requirements.txt
```

## How to run

```bash
python demo.py
```

## Expected result

The script will load three sample sentences, generate their embeddings, and print the raw vector shapes and a sample of the underlying data. You will see that regardless of the sentence length, the resulting vector has a fixed dimension (384 dimensions for the `all-MiniLM-L6-v2` model used in this demonstration).
