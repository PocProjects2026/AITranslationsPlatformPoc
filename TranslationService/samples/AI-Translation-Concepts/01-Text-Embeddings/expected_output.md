# Expected Output: Text Embeddings

When you execute `demo.py`, your console output should closely resemble the following:

```text
Initializing embedding model: 'all-MiniLM-L6-v2'...

--- Generating Embeddings ---

Original Sentence: 'The package has been shipped and is on its way.'
Vector Data Type:  <class 'numpy.ndarray'>
Vector Shape:      (384,) (Number of Dimensions)
First 10 values:   [-0.0461, 0.0827, 0.0142, -0.0632, -0.0125, 0.0384, 0.0091, 0.0543, -0.0392, 0.0159, ...]

Original Sentence: 'Please reset your password using the link sent to your email.'
Vector Data Type:  <class 'numpy.ndarray'>
Vector Shape:      (384,) (Number of Dimensions)
First 10 values:   [0.0123, -0.0456, 0.0789, 0.0234, -0.0912, -0.0432, 0.0675, -0.0213, 0.0567, -0.0876, ...]

Original Sentence: 'Your subscription will automatically renew on the 1st of next month.'
Vector Data Type:  <class 'numpy.ndarray'>
Vector Shape:      (384,) (Number of Dimensions)
First 10 values:   [-0.0765, 0.0345, -0.0890, 0.0456, 0.0123, 0.0678, -0.0543, 0.0987, -0.0321, 0.0765, ...]

Demonstration complete.
Conclusion: Sentences of varying lengths have been successfully converted into uniform fixed-length numerical vectors.
```

*(Note: The exact floating-point values will differ based on the specific environment and model initialization, but the structure and shape will match.)*

## Why this output is correct

1.  **Vector Shape `(384,)`:** The `all-MiniLM-L6-v2` model is designed to produce 384-dimensional vectors. This demonstrates that regardless of how long or short the input sentence is, the output space remains structurally identical.
2.  **Data Type:** The output is a `numpy.ndarray`, which is the standard format for handling matrix math and vector calculations in Python.
3.  **Values:** The values are floating-point numbers typically ranging between -1 and 1. These represent coordinates in the 384-dimensional semantic space. 

## How to interpret it

You are looking at the raw data format that makes semantic search possible. While these numbers are meaningless to a human reader, they allow downstream systems to compute distance metrics (like cosine similarity) to determine how closely related two sentences are.
