# Expected Output: Top-k Retrieval

When you execute `demo.py`, you will see three distinct tables printed to your console, representing different `k` values.

```text
Target Query: 'How do I change my password?'

--- Top-5 Retrieved Results ---
+--------+------------------------------------------------+--------------+
|   Rank | Message                                        |   Similarity |
+========+================================================+==============+
|      1 | Update your password in the security settings. |       0.8523 |
+--------+------------------------------------------------+--------------+
|      2 | Reset your account password.                   |       0.7641 |
+--------+------------------------------------------------+--------------+
|      3 | I forgot my password.                          |       0.6912 |
+--------+------------------------------------------------+--------------+
|      4 | Click here to change your login credentials.   |       0.6405 |
+--------+------------------------------------------------+--------------+
|      5 | Your password has expired.                     |       0.5532 |
+--------+------------------------------------------------+--------------+

--- Top-3 Retrieved Results ---
+--------+------------------------------------------------+--------------+
|   Rank | Message                                        |   Similarity |
+========+================================================+==============+
|      1 | Update your password in the security settings. |       0.8523 |
+--------+------------------------------------------------+--------------+
|      2 | Reset your account password.                   |       0.7641 |
+--------+------------------------------------------------+--------------+
|      3 | I forgot my password.                          |       0.6912 |
+--------+------------------------------------------------+--------------+
```

*(A larger Top-10 table will also follow in your actual console output.)*

## Why this output is correct

1.  **Consistency:** The mathematical ranking never changes. Rank 1 is always *"Update your password..."* regardless of whether `k=3` or `k=10`. The `k` parameter does not change the math; it only changes where we draw the cutoff line.
2.  **Noise Filtering:** Look closely at your console's Top-10 output. You will notice that ranks 7 through 10 are likely completely unrelated to passwords (e.g., server maintenance, package delivery). By using a smaller `k` (like 3 or 5), we successfully prevented that irrelevant "noise" from infiltrating our dataset.

## How to interpret it

Think of Top-k as a valve. You want to open the valve enough to let context flow through to the LLM, but not so much that you flood the system with garbage data. In production, engineers often run A/B tests to determine the optimal `k` value for their specific use case, balancing token costs against translation quality.
