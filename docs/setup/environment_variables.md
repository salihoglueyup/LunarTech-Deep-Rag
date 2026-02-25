# Environment Variables

LunarTech uses a `.env` file to manage secrets securely. Below is a comprehensive list and explanation of every variable used by the system.

## AI Models

- `OPENROUTER_API_KEY`: Highly recommended. Used to route traffic to Grok, Gemini, Anthropic, and OpenAI.
- `GEMINI_API_KEY`: Used as a direct fallback for the `flash` models when OpenRouter fails.

## Supabase (Auth & Database)

- `SUPABASE_URL`: The REST URL pointing to your Supabase instance.
- `SUPABASE_KEY`: Your Supabase `anon` or `service_role` key. Needed to bypass RLS internally.

## System Configuration

- `PORT`: (Optional) The port Streamlit runs on.
- `DEBUG_MODE`: Set to `True` for verbose console logs during Agent execution.
- `OLLAMA_HOST`: (Optional) If running Ollama on a different network IP. Defaults to `http://localhost:11434`.
