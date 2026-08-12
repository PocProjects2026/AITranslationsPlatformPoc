# Expected Output: Using Retrieved Examples as Context

When you execute `demo.py`, the console will output the exact text string that a backend server would POST to an LLM API (such as OpenAI's GPT-4 or Anthropic's Claude).

```text
============================================================
 FINAL PROMPT DELIVERED TO LLM API
============================================================
You are a professional software localization expert.
Translate the user's message into French.
Use the provided historical translations as context to maintain consistent terminology.
Do not copy the examples directly unless they are an exact match. You must generate a new, accurate translation based on the provided context.

--- HISTORICAL CONTEXT ---
Example 1:
English:     Battery level is low.
Translation: Le niveau de la batterie est faible.

Example 2:
English:     Please connect the charger.
Translation: Veuillez brancher le chargeur.

Example 3:
English:     Device battery is almost empty.
Translation: La batterie de l'appareil est presque vide.


--- USER MESSAGE ---
The battery is running low. Please connect to the charger.

TRANSLATION:
============================================================

Engineering Insight:
The LLM now possesses both instructions and specialized vocabulary (e.g., 'faible', 'chargeur').
The retrieved examples are CONTEXT ONLY. They guide the model's stylistic choices,
ensuring it generates a translation consistent with previous enterprise data,
rather than hallucinating a generic dictionary translation.
```

## Why this output is correct

1.  **Relevance:** The semantic search successfully identified the three historical translations that deal with batteries and chargers, ignoring the irrelevant records about networks and subscriptions.
2.  **Strict Formatting:** The prompt utilizes clear delimiters (`--- HISTORICAL CONTEXT ---` and `--- USER MESSAGE ---`). This prevents the LLM from getting confused about what it is supposed to translate versus what is simply reference material.
3.  **Synthesis:** Notice that the `USER MESSAGE` is actually a combination of concepts found in Example 1 and Example 2. Because of this context, the LLM will effortlessly generate a synthesis string like: *"Le niveau de la batterie est faible. Veuillez brancher le chargeur."*

## How to interpret it

This final string represents the entire purpose of the Retrieval-Augmented Generation architecture. All the vector math, cosine similarity, and top-k filtering from the previous modules existed solely to safely construct this specific block of text. By feeding an LLM high-quality, highly relevant context, we constrain its output to meet strict engineering and business requirements.
