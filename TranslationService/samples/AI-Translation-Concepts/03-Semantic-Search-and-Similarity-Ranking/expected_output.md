# Expected Output: Semantic Search and Similarity Ranking

When you execute `demo.py`, your console output should render a table similar to the following:

```text
Loading embedding model (all-MiniLM-L6-v2)...

Embedding 8 database messages...
Embedding query: 'I can't log in to my account.'...

Computing cosine similarity and ranking results...

+----------+----------------------------------------------------+--------------------+
| Rank     | Message                                            |   Similarity Score |
+==========+====================================================+====================+
| --> 1 <--| ** Account login failed due to incorrect credentials. **|             0.7351 |
+----------+----------------------------------------------------+--------------------+
| 2        | Unable to access user account.                     |             0.6932 |
+----------+----------------------------------------------------+--------------------+
| 3        | Password reset instructions have been sent.        |             0.4120 |
+----------+----------------------------------------------------+--------------------+
| 4        | Welcome to the platform, your registration is complete.|             0.2845 |
+----------+----------------------------------------------------+--------------------+
| 5        | Please update your billing information.            |             0.1450 |
+----------+----------------------------------------------------+--------------------+
| 6        | The server is currently down for maintenance.      |             0.1205 |
+----------+----------------------------------------------------+--------------------+
| 7        | Your payment was declined by the bank.             |             0.0864 |
+----------+----------------------------------------------------+--------------------+
| 8        | The package has been successfully delivered.       |             0.0210 |
+----------+----------------------------------------------------+--------------------+
```

## Why this output is correct

1.  **Top Rank:** The query *"I can't log in to my account."* does not share the exact keywords with *"Account login failed due to incorrect credentials."* (apart from "account"), yet the system successfully identified it as the most semantically equivalent concept, giving it the highest score.
2.  **Second Rank:** *"Unable to access user account."* is also highly relevant, scoring closely behind.
3.  **Low Ranks:** Completely unrelated concepts like package delivery or server maintenance naturally sink to the bottom of the list with scores approaching zero, indicating vector orthogonality (they point in completely different directions).

## How to interpret it

This table represents the raw logic of an AI search engine. The `Similarity Score` acts as a confidence metric. In a production pipeline, an engineer might set a threshold rule: *If the top Similarity Score is > 0.70, immediately return that historical translation to the user. If it is < 0.70, generate a completely new translation using an LLM.*
