# 06 - Using Retrieved Examples as Context

This final module demonstrates the culmination of the Retrieval-Augmented Generation (RAG) pipeline: taking the Top-k retrieved records and injecting them into a **System Prompt** for a Large Language Model (LLM).

## What this concept is

Once we have successfully found the historical records mathematically closest to the user's query, we must present those records to an LLM. We do this by constructing a rigid text template that separates system instructions, historical context, and the new user request.

## Why it exists

LLMs are highly capable of translating text, but left to their own devices, they will generate generic translations. An enterprise translation platform requires strict consistency in terminology. By injecting historical translations directly into the prompt as "Context," we force the LLM to learn the company's specific tone and vocabulary at runtime (a technique known as few-shot prompting or in-context learning).

## Where it is used

This is the final step immediately before calling the OpenAI API, Anthropic API, or a locally hosted model like Llama 3. The output of this script is the exact payload sent over the network to generate the final response.

## Learning objectives

*   Understand how to format a prompt for an LLM safely.
*   Differentiate between System Instructions, Context, and User Input.
*   Recognize that retrieved examples serve as guidance, not literal templates to be copied blindly.

## Required libraries

*   `sentence-transformers`
*   `numpy`
*   `scikit-learn`

## Installation

```bash
pip install -r requirements.txt
```

## How to run

```bash
python demo.py
```

## Expected result

The script will embed a user query, perform a Top-k retrieval against a mock Translation Memory, and then assemble a complete LLM prompt. The console will print the exact, formatted string that is ready to be sent to a generative AI endpoint.
