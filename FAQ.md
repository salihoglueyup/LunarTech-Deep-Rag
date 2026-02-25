# ❓ Frequently Asked Questions (FAQ)

Here are the most common questions regarding the operation, architecture, and deployment of LunarTech Deep RAG.

### 1. Is my data sent to OpenAI or Google?

**It depends on your configuration.**
By default, LunarTech routes prompt completions through OpenRouter (using models like Grok or Gemini). Your prompts and document extracts are sent to those APIs.
However, LunarTech is built to be **100% capable of offline execution**. If you pull an Ollama model locally (`ollama run llama3.1`) and select it in the sidebar, your data **never leaves your machine**.

### 2. Why does the Knowledge Graph look empty?

The Knowledge Graph relies on named entity extraction. If you uploaded a document that is very short, or highly numerical without clear logical relationships, the LLM might decide there are no "Entities" worth mapping. Alternatively, verify that your PDF contains selectable text and is not just scanned images.

### 3. I get a `TimeoutError` when using AgentWrite for Handbooks. Why?

AgentWrite spawns immense, highly-complex prompts. If you are using a slower model (or a heavily congested API during peak hours), the API provider might close the connection before it finishes computing the 4000-token output.
**Solution:** Navigate to the LLM Router settings and switch to a highly-available, extremely fast inference model like `gemini-2.5-flash` instead of `grok-2-1212` for heavy Handbook generation tasks.

### 4. Can I use this for my company/commercial product?

Yes! LunarTech is released under the **MIT License**. You are free to fork it, modify it, host it internally for your enterprise, or use it as the base for a commercial SaaS product, provided you include the original MIT license notice.

### 5. What makes "Deep RAG" better than normal RAG?

"Normal" RAG chunks text and stores it as pure numeric vectors. If you upload a book on Tesla, and ask "Summarize Elon Musk's global strategy", standard RAG will just find the 5 paragraphs where those words appear closest together.
**Deep RAG (powered by LightRAG)** builds a graph. It knows Elon Musk -> is CEO of -> Tesla -> operates in -> Global Markets. It searches the graph's structural communities, allowing it to provide a highly accurate, holistic summary spanning the entire document, rather than just 5 isolated paragraphs.

### 6. Do I need Supabase?

Yes. Currently, User Authentication, Row-Level Security mappings, workspace sharing, and chat-history persistence are hardcoded to utilize the Supabase Database stack. You can either use their managed cloud service (which has a very generous free tier) or self-host your own Supabase instance via Docker.
