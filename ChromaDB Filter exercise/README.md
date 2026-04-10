### Exercise 1 — Basic Metadata Filter
**Concept:** `where` with a simple equality filter on `collection.get()`

Retrieve all documents where `category == "vpn"` using a `where` filter.
**Expected:** 3 documents — `doc-000`, `doc-001`, `doc-002`

---

### Exercise 2 — Combined Metadata Filters
**Concept:** `$and` and `$or` logical operators

**Task A:** Retrieve documents where `priority == "high"` AND `year == 2025` AND `verified == True`.
**Expected:** 7 documents spanning vpn, email, network, and accounts categories

**Task B (Extension):** Retrieve documents where `category == "software"` OR `category == "printing"`.
**Expected:** 6 documents

---

### Exercise 3 — Full Text Search
**Concept:** `where_document` with `$contains` and `$not_contains`

> Note: `$contains` is a substring match — it finds the exact string, not semantic meaning.

**Task A:** Find all documents whose text contains the word `"student"`.

**Task B (Extension):** Narrow results to documents that contain `"student"` but do NOT contain `"password"`. Compare the count to Task A — how many were excluded?
    
    - No results were excluded, as the words `"student"`and `"password"` are not present in same documents.

---

### Exercise 4 — Semantic Query + Combined Filters
**Concept:** `collection.query()` (semantic search) combined with both `where` and `where_document`

Run a semantic query for `"how do I print documents on campus"` restricted to:
- `category == "printing"` (using `where`)
- Document text must contain `"page"` (using `where_document`)
- Request `n_results=5` and include distances

**Reflection questions:**
- How many results are returned? Why might it be fewer than `n_results=5`?
    - 2 documents are returned as a result. 'n_results' sets the maximum number of documents returned. If documents found is less tha 'n_results', ChromaDB returns however many documents exists.
- Are the distance values close to 0 or far from 0? What does that tell you?
    - Distance on both documents is over 1. This tells me that semantically the contents of these documents are not quite what the prompt was looking for.
- Remove the `where` filter and run again — how does the result set change?
    - There is no change to the result, as only the two documents contain the word '"page"'.


## Bonus Challenges

1. Use `$gte` to find all documents from `year >= 2025`
2. Use `$in` to find documents where `priority` is `"high"` or `"medium"`
3. Combine metadata and text filters: find high-priority documents containing the word `"MFA"`
4. Use `collection.get(include=[])` to retrieve only document IDs (no text, no metadata) — when is this useful?