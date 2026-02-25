# Deep RAG & Knowledge Graphs

At the heart of the LunarTech document processing engine lies a custom integration of **LightRAG**, providing a hybrid intelligence model replacing naive vector search.

## How it works

1. **Document Ingestion**
   When a user uploads a PDF or DOCX file, the `document_processor` segments the text into distinct, semantically cohesive chunks.

2. **Vectorization**
   Instead of relying on single-provider embeddings, the system is designed to use BGE models or HuggingFace fallback embeddings via OpenRouter to create dense vector representations.

3. **Entity and Relation Extraction**
   This is the differentiator. As text is processed, an LLM scans the chunks to extract specific "Entities" (e.g., "Artificial Intelligence", "Elon Musk", "Tesla") and maps the "Relations" between them (e.g., "Elon Musk -> CEO -> Tesla").

4. **Graph Construction**
   The extracted data points formulate a massive graph (`graph_chunk_entity_relation.graphml`). This graph is directly visualized in the **Knowledge Graph** interface.

## Retrieval Process

When the user asks a question, the system does not just search for semantic similarity. It conducts:

- **Local Search:** Finding nodes closely related to the exact keywords.
- **Global Search:** Finding overarching community structures within the graph to answer high-level "summary" questions.
- **Hybrid Search:** Combining Vector exactness with Graph contextual nuance.

This approach virtually eliminates hallucinations and ensures the LLM grounds its answers explicitly in the uploaded corpus.
