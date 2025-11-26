# Collections Feature Guide

## Overview
The RAG application now supports **collections** - a partitioning feature that allows you to organize documents by topic, category, or any logical grouping. This significantly speeds up queries by searching only within relevant collections instead of the entire database.

## Key Benefits
- **Faster Queries**: Search only within specific collections instead of all documents
- **Better Organization**: Group related documents together (e.g., "medical", "programming", "legal")
- **Improved Accuracy**: More focused context leads to better answers
- **Scalability**: As your database grows, collections keep queries fast

## How to Use Collections

### 1. Upload Documents to Collections

When uploading a document, you can:

**Option A: Select Existing Collection**
1. Open the File Upload section
2. Use the "Collection" dropdown to select from existing collections
3. Upload your document

**Option B: Create New Collection**
1. Open the File Upload section
2. Click "New Collection" button
3. Enter a new collection name (e.g., "medical", "programming", "finance")
4. Upload your document

**Default Behavior**: If no collection is selected, documents go to the "default" collection.

### 2. Query Within Collections

When asking questions:

1. Open the Query Interface section
2. Select the collection to search from the "Collection" dropdown
3. Enter your question
4. The system will search only within that collection

### 3. View Collection Statistics

The query results show:
- **Collection Used**: Which collection was searched
- **Total Chunks in DB**: How many chunks exist in that collection
- **Chunks Used**: How many chunks were used to answer your question
- **Relevance**: Percentage of collection chunks used

## Example Use Cases

### Use Case 1: Multi-Department Knowledge Base
```
Collections:
- "hr_policies" → HR manuals, employee handbooks
- "engineering" → Technical documentation, API guides
- "sales" → Product sheets, pricing documents
```

When an engineer asks about API authentication, search only "engineering" collection for faster, more relevant results.

### Use Case 2: Multi-Language Documentation
```
Collections:
- "docs_english" → English documentation
- "docs_spanish" → Spanish documentation
- "docs_french" → French documentation
```

Route queries to language-specific collections automatically.

### Use Case 3: Time-Based Partitioning
```
Collections:
- "policies_2024" → Current year policies
- "policies_2023" → Last year policies
- "archive" → Historical documents
```

Query recent documents first for best performance.

## Testing the Feature

### Step 1: Upload Test Documents

1. Upload `test_documents/medical_terminology.txt` to collection "medical"
2. Upload `test_documents/programming_concepts.txt` to collection "programming"

### Step 2: Test Queries

**Query 1 - Medical Collection**
- Collection: "medical"
- Question: "What is the difference between acute and chronic?"
- Expected: Fast answer using only medical documents

**Query 2 - Programming Collection**
- Collection: "programming"
- Question: "What are the main principles of OOP?"
- Expected: Fast answer using only programming documents

**Query 3 - Wrong Collection**
- Collection: "medical"
- Question: "What is polymorphism?"
- Expected: No good answer (programming concept searched in medical docs)

### Step 3: View Collections

Check the collections endpoint:
```bash
curl http://localhost:8000/collections
```

Expected response:
```json
{
  "collections": {
    "medical": 5,
    "programming": 7,
    "default": 8
  },
  "total_collections": 3,
  "total_documents": 20
}
```

## API Endpoints

### List All Collections
```bash
GET /collections
```

### Get Collection Info
```bash
GET /collections/{collection_name}
```

### Delete Collection
```bash
DELETE /collections/{collection_name}
```

### Upload with Collection
```bash
POST /upload?collection=medical
```

### Query within Collection
```bash
POST /query
{
  "query": "What is diagnosis?",
  "num_results": 5,
  "collection": "medical"
}
```

## Best Practices

1. **Meaningful Names**: Use descriptive collection names that reflect content type
2. **Consistent Naming**: Use lowercase, underscores for multi-word names (e.g., "hr_policies")
3. **Logical Grouping**: Group documents that would typically be searched together
4. **Don't Over-Partition**: Too many tiny collections can be inefficient
5. **Default Collection**: Use "default" for general documents that don't fit specific categories

## Performance Comparison

### Without Collections
- Search ALL 1000 documents every query
- Slower as database grows
- May retrieve irrelevant context

### With Collections
- Search only 50 documents in "medical" collection
- 20x faster queries
- More relevant context and better answers

## Technical Details

- **Vector Store**: Each collection has its own FAISS index
- **Storage**: Collections stored in `faiss_db/{collection_name}/`
- **Isolation**: Collections are completely independent
- **Scalability**: Linear scaling with number of collections

## Troubleshooting

**Q: My collection isn't showing up**
A: Refresh the page or check `/collections` endpoint

**Q: Query returns no results**
A: Verify you're searching the correct collection

**Q: How do I move documents between collections?**
A: Currently, re-upload the document to the new collection and delete from old

**Q: Can I search multiple collections at once?**
A: Not currently - select one collection per query

## Future Enhancements

- Multi-collection search
- Collection management UI (rename, merge, move documents)
- Auto-collection suggestion based on document content
- Collection-level access controls
