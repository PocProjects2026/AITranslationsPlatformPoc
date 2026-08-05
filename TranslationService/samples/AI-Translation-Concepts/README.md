# AI Translation Concepts Educational Project

Welcome to the AI Translation Concepts Educational Project. This repository serves as a practical, code-first curriculum designed to demystify the internal workings of modern AI-driven translation platforms.

The project is structured into six independent modules. Each module covers a distinct engineering concept, moving from fundamental text embeddings to constructing contextual prompts for Large Language Models.

## Core Objective

The primary goal is to bridge the gap between theoretical machine learning concepts and applied software engineering. Rather than relying on abstract mathematics alone, this project provides runnable Python implementations that simulate how a production translation system processes, retrieves, and utilizes historical translation data.

## Project Structure

*   **01-Text-Embeddings:** Translating human-readable text into dense vector representations.
*   **02-Vector-Normalization-Cosine-Similarity:** Standardizing vectors and measuring mathematical distance.
*   **03-Semantic-Search-and-Similarity-Ranking:** Comparing query vectors against a database to find the closest semantic matches.
*   **04-Top-K-Retrieval:** Filtering ranked results to isolate the most relevant context.
*   **05-Exact-vs-Semantic-Matching:** Deciding when to use deterministic hash lookups versus probabilistic vector search.
*   **06-Using-Retrieved-Examples-as-Context:** Formatting retrieved translations into structured prompts to guide an LLM's output.

## How to Use This Project

Each folder is completely standalone. You can open any directory, read the `README.md`, and execute the demonstration script without needing to run the prior modules.

1.  Navigate into a concept folder (e.g., `cd 01-Text-Embeddings`).
2.  Review the `README.md` and `explanation.md` for context and theory.
3.  Install the required dependencies (`pip install -r requirements.txt`).
4.  Run the demonstration script (`python demo.py`).
5.  Compare the console output against the `expected_output.md` file.

All scripts use localized sample data to ensure execution without requiring external API keys, database connections, or cloud resources.
