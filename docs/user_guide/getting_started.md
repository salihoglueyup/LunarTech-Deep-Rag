# Getting Started with LunarTech Deep RAG

Welcome to **LunarTech Deep RAG**! This platform is more than just a chat interface; it's a productivity operating system designed around large language models and structured document generation.

## 1. Uploading Documents

Everything starts with your data.
Navigate to the **Sidebar** on the left. You will see a file uploader labeled `Upload PDF`.
Drag and drop your PDFs, DOCX, TXT, or MD files here.

Once uploaded, the underlying `LightRAG` engine will chunk your text, run semantic embeddings, and extract the entities/relationships into the global **Knowledge Graph**.

## 2. Navigating the Views

The sidebar provides navigation to different core experiences:

- **Chat**: A familiar ChatGPT-like interface. However, it queries your specific documents utilizing the Deep RAG hybrid search.
- **Handbook**: Want to write a 100-page book on a topic based on your PDFs? Use the AgentWrite handbook generator here.
- **Knowledge Graph**: Visually explore the connections extracted from your documents in a 3D interface.
- **Swarm Studio**: Create completely custom AI agents, grant them internet/database tools, and chain them together into an execution pipeline.
- **Shadow Agents**: Send autonomous tasks to the background (e.g., "Scrape this website every 60 minutes").

## 3. Team Collaboration

In the **Advanced Settings** dropdown on the sidebar, you can enter a `Team Code`. Sharing this code with your colleagues merges your document pools and chat histories, providing a unified workspace.
