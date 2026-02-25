# Setup and Installation

This guide will walk you through setting up **LunarTech Deep RAG** on your local machine. Because this is a heavy-duty AI system, it requires several API integrations and local software setups.

## Prerequisites

- **Python 3.10+**
- **Git**
- **Node.js** (Optional, if you wish to run some external web scraping tools).

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lunartech-deep-rag.git
cd lunartech-deep-rag
```

## 2. Install Python Dependencies

It is highly recommended to use a virtual environment.

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On MacOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Environment Variables

Create a `.env` file in the root directory. You can copy the template:

```bash
cp .env.example .env
```

Fill in the following keys in your `.env`:

- `OPENROUTER_API_KEY`: Required for Grok/Gemini access.
- `SUPABASE_URL` and `SUPABASE_KEY`: Required for authentication and document tracking.

## 4. Run the Application

Start the Streamlit interface:

```bash
streamlit run app/main.py
```

And access the dashboard at `http://localhost:8501`.

## Local LLM Setup (Optional)

If you wish to run entirely offline, download and install [Ollama](https://ollama.ai/). Ensure Ollama is running, then pull a model:

```bash
ollama run llama3.1
```

The application will automatically detect the local port `11434` and allow you to select local models from the sidebar.
