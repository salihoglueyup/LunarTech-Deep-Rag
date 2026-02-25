# Troubleshooting Guide

While LunarTech Deep RAG is designed with extreme fault tolerance, the reliance on external LLM APIs and local Graph databases can sometimes cause issues. Here is how to resolve the most common problems.

## 1. Streamlit `TypeError: 'NoneType' object is not subscriptable`

**Symptom**: You click a button in the UI, and a large red error box appears.
**Cause**: The API quota for OpenRouter or Gemini has been exhausted, and the fallback LLM returned `None` instead of a valid JSON string.
**Fix**:

1. Check your terminal logs (`DEBUG_MODE=True`).
2. Verify you have credits on your OpenRouter account.
3. If running locally, ensure Ollama is actively running (`ollama serve`).

## 2. Background Tasks (Shadow Agents) are stuck in "Pending"

**Symptom**: You submit a Shadow Agent task, but it never moves to "Running".
**Cause**: The background polling thread has crashed or requires a restart.
**Fix**:
Restart the main Streamlit application. The background worker automatically boots up and resumes any "pending" tasks seamlessly upon start.

## 3. Empty Knowledge Graph

**Symptom**: You uploaded a document, but the Knowledge Graph tab is completely blank.
**Cause**: LightRAG failed to extract entities. This usually happens if the uploaded document contains scanned images without OCR (it's pure image, no text).
**Fix**: Ensure your PDFs contain actual selectable text. You can verify this by trying to highlight the text in a standard PDF viewer.

## 4. `Supabase AuthError` on Login

**Symptom**: Cannot login using standard credentials.
**Fix**: Verify that your `.env` contains the correct `SUPABASE_URL` and `SUPABASE_KEY`. Ensure the database hasn't been paused by Supabase due to inactivity.
